"""
Base Agent class.
Provides common functionality for all specialized agents.
"""
import os
import json
import logging
from typing import Any, Dict, Optional

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

logger = logging.getLogger(__name__)


class BaseAgent:
    """
    Base class for all travel agents.
    Provides shared LLM client and utility methods.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize base agent with OpenAI client.
        
        Args:
            api_key: OpenAI API key (optional, can be set via env var)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = None
        
        if OpenAI and self.api_key:
            try:
                self.client = OpenAI(api_key=self.api_key)
                logger.info(f"{self.__class__.__name__} initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI client: {e}")
        else:
            logger.warning(f"{self.__class__.__name__} initialized without OpenAI client")
    
    def call_llm(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        model: str = "gpt-3.5-turbo",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        response_format: Optional[str] = None
    ) -> str:
        """
        Call LLM with a prompt and return the response.
        
        Args:
            prompt: User prompt
            system_message: Optional system message
            model: Model name
            temperature: Temperature (0-1)
            max_tokens: Maximum tokens to generate
            response_format: Optional response format (e.g., "json_object")
        
        Returns:
            LLM response text
        """
        if not self.client:
            raise RuntimeError("OpenAI client not initialized")
        
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})
        
        kwargs = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
        }
        
        if max_tokens:
            kwargs["max_tokens"] = max_tokens
        
        if response_format == "json_object":
            kwargs["response_format"] = {"type": "json_object"}
        
        try:
            response = self.client.chat.completions.create(**kwargs)
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            raise
    
    def safe_json_parse(self, text: str, default: Any = None) -> Any:
        """
        Safely parse JSON from text.
        
        Args:
            text: Text to parse
            default: Default value if parsing fails
        
        Returns:
            Parsed JSON or default value
        """
        try:
            # Try to extract JSON if wrapped in markdown code blocks
            if "```json" in text:
                start = text.find("```json") + 7
                end = text.find("```", start)
                text = text[start:end].strip()
            elif "```" in text:
                start = text.find("```") + 3
                end = text.find("```", start)
                text = text[start:end].strip()
            
            return json.loads(text)
        except json.JSONDecodeError as e:
            logger.warning(f"JSON parse failed: {e}. Text: {text[:200]}")
            return default if default is not None else {}
    
    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text.
        Very rough approximation: 1 token ≈ 4 characters.
        
        Args:
            text: Text to estimate
        
        Returns:
            Estimated token count
        """
        return len(text) // 4
