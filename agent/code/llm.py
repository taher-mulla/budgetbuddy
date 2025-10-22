"""
LLM Integration Module

Handles connection to AWS Bedrock and LLM invocation.
"""

import boto3
import json
import os
from enum import Enum
from typing import Optional


class LLMProvider(str, Enum):
    """Supported LLM providers"""
    CLAUDE = "claude"


class LLM:
    """
    AWS Bedrock LLM client
    
    Simple interface for invoking LLMs through Bedrock.
    """
    
    def __init__(
        self,
        provider: str = "claude",
        model_id: Optional[str] = None,
        region: str = "us-east-1"
    ):
        """
        Initialize LLM client
        
        Args:
            provider: LLM provider string (currently only "claude")
            model_id: Specific model ID (defaults to Claude 3.5 Sonnet)
            region: AWS region
        """
        # Convert string to enum
        try:
            self.provider = LLMProvider(provider.lower())
        except ValueError:
            print(f"Warning: Unsupported provider '{provider}'. Falling back to default provider 'claude'.")
            self.provider = LLMProvider.CLAUDE
        
        self.region = region
        
        # Set model ID based on provider
        if model_id:
            self.model_id = model_id
        elif self.provider == LLMProvider.CLAUDE:
            self.model_id = os.getenv(
                "BEDROCK_MODEL_ID",
                "anthropic.claude-3-5-sonnet-20241022-v2:0"
            )
        
        # Initialize Bedrock client
        self.client = boto3.client("bedrock-runtime", region_name=self.region)
    
    def invoke(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.0,
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Invoke LLM with prompt
        
        Args:
            prompt: User prompt/question
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature (0 = deterministic)
            system_prompt: Optional system prompt for context
            
        Returns:
            LLM response text
        """
        if self.provider == LLMProvider.CLAUDE:
            return self._invoke_claude(prompt, max_tokens, temperature, system_prompt)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
    
    def _invoke_claude(
        self,
        prompt: str,
        max_tokens: int,
        temperature: float,
        system_prompt: Optional[str]
    ) -> str:
        """Invoke Claude through Bedrock"""
        
        # Build request body
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        
        # Add system prompt if provided
        if system_prompt:
            body["system"] = system_prompt
        
        # Invoke model
        response = self.client.invoke_model(
            modelId=self.model_id,
            body=json.dumps(body)
        )
        
        # Parse response
        response_body = json.loads(response["body"].read())
        return response_body["content"][0]["text"]

