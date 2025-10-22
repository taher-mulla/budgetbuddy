"""
AWS Lambda Handler for BudgetBuddy Expense Agent

Entry point for processing expense requests from the frontend.
"""

import json
import os
import sys

# Add current directory to path for local imports
sys.path.append(os.path.dirname(__file__))

from agent import ExpenseAgent


# Initialize agent (reused across Lambda invocations)
agent = None


def lambda_handler(event, context):
    """
    Main Lambda handler for processing expense requests
    
    Expected event from API Gateway:
    {
        "body": "{\"text\": \"add thirty dollars for groceries\", \"timestamp\": \"...\"}",
        "headers": {...},
        "requestContext": {...}
    }
    
    Returns:
    {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": "{\"status\": \"success\", \"message\": \"...\"}"
    }
    """
    
    global agent
    
    print(f"Received event: {json.dumps(event)}")
    
    try:
        # Initialize agent on first invocation
        if agent is None:
            agent = ExpenseAgent(
                config_path="agent_config.xml",
                prompts_path="prompts.xml"
            )
        
        # Parse request body
        body = json.loads(event.get("body", "{}"))
        text = body.get("text", "").strip()
        user_id = body.get("user_id", "me")
        
        # Validate input
        if not text:
            return create_response(400, {
                "error": "Text field is required",
                "message": "Please provide expense text"
            })
        
        print(f"Processing expense for user '{user_id}': {text}")
        
        # Process expense with agent
        result = agent.process_expense(text, user_id)
        
        return create_response(200, result)
        
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {str(e)}")
        return create_response(400, {
            "error": "Invalid JSON in request body",
            "details": str(e)
        })
        
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return create_response(500, {
            "error": "Internal server error",
            "details": str(e)
        })


def create_response(status_code: int, body: dict) -> dict:
    """
    Create standardized API Gateway response
    
    Args:
        status_code: HTTP status code
        body: Response body (will be JSON serialized)
    
    Returns:
        API Gateway response dict
    """
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",  # Update with specific domain in production
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Methods": "POST, OPTIONS"
        },
        "body": json.dumps(body)
    }


# For local testing
if __name__ == "__main__":
    # Test event
    test_event = {
        "body": json.dumps({
            "text": "add thirty dollars for groceries",
            "timestamp": "2025-10-22T00:00:00Z"
        })
    }
    
    response = lambda_handler(test_event, None)
    print(f"\nResponse: {json.dumps(json.loads(response['body']), indent=2)}")
