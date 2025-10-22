"""
Utility Module

Common utility functions for the agent.
"""

import json
import re
from typing import Dict, Any, Optional


def parse_json_from_text(text: str) -> Optional[Dict[str, Any]]:
    """
    Extract and parse JSON from text that may contain other content
    
    Args:
        text: Text that may contain JSON
        
    Returns:
        Parsed JSON dict or None if no valid JSON found
    """
    # Try parsing the whole text first
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        pass
    
    # Try finding JSON in text with regex
    json_pattern = r'\{[^{}]*\}'
    matches = re.findall(json_pattern, text)
    
    for match in matches:
        try:
            return json.loads(match)
        except json.JSONDecodeError:
            continue
    
    # Try finding JSON in code blocks
    code_block_pattern = r'```(?:json)?\s*(\{.*?\})\s*```'
    matches = re.findall(code_block_pattern, text, re.DOTALL)
    
    for match in matches:
        try:
            return json.loads(match)
        except json.JSONDecodeError:
            continue
    
    return None


def load_config(config_path: str) -> Dict[str, Any]:
    """
    Load configuration from YAML file
    
    Args:
        config_path: Path to config file
        
    Returns:
        Configuration dictionary
    """
    import yaml
    
    with open(config_path, 'r') as file:
        try:
            config = yaml.safe_load(file)
            return config
        except yaml.YAMLError as exc:
            print(f"Error parsing YAML config: {exc}")
            return {}


def load_prompts(prompts_path: str) -> Dict[str, str]:
    """
    Load prompts from YAML file
    
    Args:
        prompts_path: Path to prompts file
        
    Returns:
        Dictionary of prompt templates
    """
    import yaml
    
    with open(prompts_path, 'r') as file:
        try:
            prompts = yaml.safe_load(file)
            return prompts
        except yaml.YAMLError as exc:
            print(f"Error parsing YAML prompts: {exc}")
            return {}


def format_currency(amount: float) -> str:
    """
    Format amount as currency
    
    Args:
        amount: Dollar amount
        
    Returns:
        Formatted string (e.g., "$30.00")
    """
    return f"${amount:.2f}"


def normalize_category(category: str, valid_categories: list) -> Optional[str]:
    """
    Normalize category name and check if valid
    
    Args:
        category: Category to normalize
        valid_categories: List of valid categories
        
    Returns:
        Normalized category or None if invalid
    """
    category = category.lower().strip()
    
    # Exact match
    if category in valid_categories:
        return category
    
    # Fuzzy match (simple substring)
    for valid_cat in valid_categories:
        if category in valid_cat or valid_cat in category:
            return valid_cat
    
    return None

