"""
Claim Detection Agent
Detects if text contains a verifiable claim
"""

import json
import os
from typing import Dict, Any, Optional
from openai import AsyncOpenAI
from loguru import logger

from .prompts import get_claim_detection_prompt


class ClaimDetectionAgent:
    """AI Agent for detecting claims in text"""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = os.getenv("LLM_MODEL", "gpt-4o")
        self.temperature = float(os.getenv("LLM_TEMPERATURE", "0.2"))
    
    async def detect_claim(self, text: str) -> Dict[str, Any]:
        """
        Detect if text contains a claim
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dictionary with claim detection results
        """
        try:
            prompt = get_claim_detection_prompt(text)
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert claim detection AI. Output only valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=self.temperature,
                max_tokens=1000,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Validate response structure
            validated_result = self._validate_response(result)
            
            logger.info(f"Claim detection: is_claim={validated_result['is_claim']}, "
                       f"confidence={validated_result['confidence']}")
            
            return validated_result
            
        except Exception as e:
            logger.error(f"Claim detection failed: {e}")
            return {
                "is_claim": False,
                "claim_text": "",
                "entities": [],
                "claim_type": "general",
                "confidence": 0.0,
                "error": str(e)
            }
    
    def _validate_response(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and normalize response"""
        return {
            "is_claim": result.get("is_claim", False),
            "claim_text": result.get("claim_text", ""),
            "entities": result.get("entities", []),
            "claim_type": result.get("claim_type", "general"),
            "confidence": max(0.0, min(1.0, result.get("confidence", 0.0))),
            "reasoning": result.get("reasoning", "")
        }
    
    async def extract_entities(self, text: str) -> list:
        """Extract entities from text"""
        try:
            prompt = f"""Extract key entities from this text. Return JSON only.

TEXT: {text}

OUTPUT FORMAT:
{{
  "entities": [
    {{"text": "entity", "type": "person/organization/location/date/number/other", "confidence": 0.0-1.0}}
  ]
}}

Extract:"""
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an entity extraction expert. Output only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=500,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return result.get("entities", [])
            
        except Exception as e:
            logger.error(f"Entity extraction failed: {e}")
            return []
