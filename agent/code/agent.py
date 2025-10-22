"""
Expense Agent Module

LangGraph-based agent for processing expense entries with LLM.
"""

import os
import json
from typing import TypedDict, Literal, Optional
from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field

from llm import LLM
from db_utils import insert_expense, get_session_state, save_session_state
from utils import (
    parse_json_from_text,
    load_config,
    load_prompts,
    format_currency,
    normalize_category
)


class ExpenseData(BaseModel):
    """Parsed expense data with validation"""
    action: str = "add"
    amount: Optional[float] = None
    category: Optional[str] = None
    note: Optional[str] = None


class AgentState(TypedDict):
    """State passed through the LangGraph workflow"""
    text: str
    parsed_data: Optional[ExpenseData]
    validation_status: Literal["pending", "valid", "invalid_category", "invalid_amount", "error"]
    clarification_needed: bool
    clarification_message: Optional[str]
    expense_id: Optional[int]
    user_id: str
    history: list


class ExpenseAgent:
    """
    LangGraph agent for processing expense entries
    
    Workflow:
    1. Parse natural language with LLM
    2. Validate parsed data
    3. Save to database if valid, or request clarification
    """
    
    def __init__(self, config_path: str = "agent_config.yaml", prompts_path: str = "prompts.yaml"):
        """
        Initialize agent
        
        Args:
            config_path: Path to configuration file
            prompts_path: Path to prompts file
        """
        # Load configuration
        self.config = load_config(config_path)
        self.prompts = load_prompts(prompts_path)
        
        # Extract config values
        llm_config = self.config.get("llm", {})
        categories_config = self.config.get("categories", {})
        
        # Initialize LLM
        self.llm = LLM(
            provider=llm_config.get("provider", "claude"),
            model_id=llm_config.get("model_id"),
            region=os.getenv("AWS_REGION", "us-east-1")
        )
        
        # Get valid categories from config
        if isinstance(categories_config, list):
            # XML parser returns list when multiple same-named tags
            self.valid_categories = categories_config
        elif isinstance(categories_config, dict):
            # Fallback for different XML structure
            self.valid_categories = list(categories_config.values())
        else:
            # Fallback to defaults
            self.valid_categories = [
                "groceries", "dining", "entertainment", 
                "transportation", "utilities", "shopping", 
                "health", "other"
            ]
        
        # Build workflow
        self.workflow = self._build_workflow()
    
    def process_expense(self, text: str, user_id: str = "me") -> dict:
        """
        Main entry point for processing expense
        
        Args:
            text: Natural language expense text
            user_id: User identifier
            
        Returns:
            Response dictionary with status and message
        """
        # Load session state
        session = get_session_state(user_id)
        
        # Initial state
        initial_state: AgentState = {
            "text": text,
            "parsed_data": None,
            "validation_status": "pending",
            "clarification_needed": False,
            "clarification_message": None,
            "expense_id": None,
            "user_id": user_id,
            "history": session.get("history", [])
        }
        
        # Run workflow
        final_state = self.workflow.invoke(initial_state)
        
        # Update history
        final_state["history"].append({
            "text": text,
            "parsed": final_state["parsed_data"].model_dump() if final_state["parsed_data"] else None,
            "status": final_state["validation_status"]
        })
        
        # Keep only last 10 history items
        if len(final_state["history"]) > 10:
            final_state["history"] = final_state["history"][-10:]
        
        # Save session state
        save_session_state(user_id, {"history": final_state["history"]})
        
        # Format response
        return self._format_response(final_state)
    
    def _build_workflow(self) -> StateGraph:
        """Build LangGraph workflow"""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("parse", self._parse_expense)
        workflow.add_node("validate", self._validate_expense)
        workflow.add_node("save", self._save_expense)
        
        # Define flow
        workflow.set_entry_point("parse")
        workflow.add_edge("parse", "validate")
        workflow.add_conditional_edges(
            "validate",
            self._route_after_validation,
            {
                "save": "save",
                "clarify": END
            }
        )
        workflow.add_edge("save", END)
        
        return workflow.compile()
    
    def _parse_expense(self, state: AgentState) -> AgentState:
        """Node: Parse natural language with LLM"""
        
        # Build prompt
        prompt = self.prompts["parse_expense"].format(
            text=state["text"],
            categories=", ".join(self.valid_categories)
        )
        
        # Call LLM
        try:
            response = self.llm.invoke(prompt)
            parsed_json = parse_json_from_text(response)
            
            if parsed_json:
                state["parsed_data"] = ExpenseData(**parsed_json)
            else:
                state["validation_status"] = "error"
                
        except Exception as e:
            print(f"Error parsing expense: {e}")
            state["validation_status"] = "error"
        
        return state
    
    def _validate_expense(self, state: AgentState) -> AgentState:
        """Node: Validate parsed expense data"""
        
        parsed = state["parsed_data"]
        
        # Check if parsing failed
        if not parsed or state["validation_status"] == "error":
            state["validation_status"] = "error"
            state["clarification_needed"] = True
            state["clarification_message"] = "I couldn't understand that. Please try again with something like 'add 30 dollars for groceries'"
            return state
        
        # Validate amount
        if not parsed.amount or parsed.amount <= 0:
            state["validation_status"] = "invalid_amount"
            state["clarification_needed"] = True
            state["clarification_message"] = self.prompts.get(
                "clarify_amount",
                "What amount did you want to add?"
            ).format(text=state["text"])
            return state
        
        # Validate and normalize category
        if parsed.category:
            normalized = normalize_category(parsed.category, self.valid_categories)
            if normalized:
                parsed.category = normalized
                state["validation_status"] = "valid"
                state["clarification_needed"] = False
            else:
                state["validation_status"] = "invalid_category"
                state["clarification_needed"] = True
                state["clarification_message"] = self.prompts.get(
                    "clarify_category",
                    f"'{parsed.category}' isn't a valid category. Choose from: {', '.join(self.valid_categories)}"
                ).format(
                    text=state["text"],
                    amount=parsed.amount,
                    category=parsed.category,
                    categories=", ".join(self.valid_categories)
                )
        else:
            # No category provided, use "other"
            parsed.category = "other"
            state["validation_status"] = "valid"
            state["clarification_needed"] = False
        
        return state
    
    def _save_expense(self, state: AgentState) -> AgentState:
        """Node: Save valid expense to database"""
        
        parsed = state["parsed_data"]
        
        try:
            expense_id = insert_expense(
                amount=parsed.amount,
                category=parsed.category,
                note=parsed.note
            )
            state["expense_id"] = expense_id
        except Exception as e:
            print(f"Error saving expense: {e}")
            state["validation_status"] = "error"
            state["clarification_needed"] = True
            state["clarification_message"] = "Sorry, there was an error saving your expense. Please try again."
        
        return state
    
    def _route_after_validation(self, state: AgentState) -> Literal["save", "clarify"]:
        """Decision: Route to save or clarification based on validation"""
        if state["clarification_needed"]:
            return "clarify"
        return "save"
    
    def _format_response(self, state: AgentState) -> dict:
        """Format final response for API"""
        
        if state["clarification_needed"]:
            return {
                "status": "clarification_needed",
                "message": state["clarification_message"]
            }
        
        if state["validation_status"] == "error":
            return {
                "status": "error",
                "message": "Sorry, something went wrong. Please try again."
            }
        
        # Success
        parsed = state["parsed_data"]
        return {
            "status": "success",
            "message": f"{format_currency(parsed.amount)} added to {parsed.category}",
            "expense_id": state["expense_id"],
            "amount": parsed.amount,
            "category": parsed.category
        }

