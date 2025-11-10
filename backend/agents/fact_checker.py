"""
Fact-Checker Agent
Main AI agent for verifying claims against evidence
"""

import json
import os
from typing import Dict, Any, List
from openai import AsyncOpenAI
from loguru import logger

from .prompts import get_fact_checker_prompt


class FactCheckerAgent:
    """AI Agent for fact-checking claims"""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = os.getenv("LLM_MODEL", "gpt-4o")
        self.temperature = float(os.getenv("LLM_TEMPERATURE", "0.2"))
        self.max_tokens = int(os.getenv("MAX_TOKENS", "2000"))
    
    async def fact_check(
        self,
        claim_text: str,
        evidence_sources: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Fact-check a claim using provided evidence
        
        Args:
            claim_text: The claim to verify
            evidence_sources: List of evidence sources
            
        Returns:
            Verdict with reasoning, sources, and metadata
        """
        try:
            # Format evidence for prompt
            evidence_formatted = self._format_evidence(evidence_sources)
            
            # Get fact-checker prompt
            prompt = get_fact_checker_prompt(claim_text, evidence_formatted)
            
            # Call LLM
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are CrisisGuard AI, an expert fact-checking system. "
                            "You must output ONLY valid JSON. Never fabricate sources. "
                            "Base verdicts strictly on provided evidence."
                        )
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Validate and normalize response
            validated_result = self._validate_verdict(result, evidence_sources)
            
            logger.info(
                f"Fact-check complete: verdict={validated_result['verdict']}, "
                f"confidence={validated_result['confidence']}, "
                f"harm_score={validated_result['harm_score']}"
            )
            
            return validated_result
            
        except Exception as e:
            logger.error(f"Fact-checking failed: {e}")
            return self._create_error_verdict(claim_text, str(e))
    
    def _format_evidence(self, evidence_sources: List[Dict[str, Any]]) -> str:
        """Format evidence sources for prompt"""
        if not evidence_sources:
            return "No evidence sources available."
        
        formatted = []
        for i, source in enumerate(evidence_sources, 1):
            formatted.append(f"""
SOURCE {i}:
Title: {source.get('title', 'N/A')}
URL: {source.get('url', 'N/A')}
Domain: {source.get('domain', 'N/A')}
Reliability: {source.get('reliability_score', 0.5):.2f}
Published: {source.get('published_date', 'Unknown')}
Excerpt: {source.get('excerpt', 'No excerpt available')[:500]}
---
""")
        
        return "\n".join(formatted)
    
    def _validate_verdict(
        self,
        result: Dict[str, Any],
        evidence_sources: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Validate and normalize verdict response"""
        
        # Validate verdict type
        valid_verdicts = ["True", "False", "Misleading", "Partially True", "Unverified"]
        verdict = result.get("verdict", "Unverified")
        if verdict not in valid_verdicts:
            verdict = "Unverified"
        
        # Validate confidence
        confidence = max(0.0, min(1.0, float(result.get("confidence", 0.0))))
        
        # Validate harm score
        harm_score = max(0, min(100, int(result.get("harm_score", 0))))
        
        # Validate recommended action
        valid_actions = ["label", "debunk", "escalate", "monitor", "approve"]
        action = result.get("recommended_action", "monitor")
        if action not in valid_actions:
            action = "monitor"
        
        # Validate sources - ensure they're from provided evidence
        sources = result.get("sources", [])
        validated_sources = self._validate_sources(sources, evidence_sources)
        
        return {
            "verdict": verdict,
            "confidence": confidence,
            "reasoning": result.get("reasoning", "")[:3000],
            "sources": validated_sources,
            "explain_like_12": result.get("explain_like_12", "")[:1000],
            "harm_score": harm_score,
            "recommended_action": action,
            "expert_explanation": result.get("reasoning", "")[:1500],
            "tags": result.get("tags", [])[:10]
        }
    
    def _validate_sources(
        self,
        claimed_sources: List[Dict[str, Any]],
        evidence_sources: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Validate that claimed sources match provided evidence
        Prevent hallucinated citations
        """
        evidence_urls = {s.get("url") for s in evidence_sources}
        
        validated = []
        for source in claimed_sources[:10]:  # Max 10 sources
            url = source.get("link", "")
            
            # Only include if URL exists in evidence
            if url in evidence_urls:
                # Find matching evidence to get reliability
                matching_evidence = next(
                    (e for e in evidence_sources if e.get("url") == url),
                    {}
                )
                
                validated.append({
                    "link": url,
                    "excerpt": source.get("excerpt", "")[:500],
                    "title": source.get("title") or matching_evidence.get("title", ""),
                    "reliability": matching_evidence.get("reliability_score", 0.5)
                })
        
        # If no valid sources, use top 3 from evidence
        if not validated and evidence_sources:
            for source in evidence_sources[:3]:
                validated.append({
                    "link": source.get("url", ""),
                    "excerpt": source.get("excerpt", "")[:500],
                    "title": source.get("title", ""),
                    "reliability": source.get("reliability_score", 0.5)
                })
        
        return validated[:10]
    
    def _create_error_verdict(self, claim_text: str, error: str) -> Dict[str, Any]:
        """Create error verdict when fact-checking fails"""
        return {
            "verdict": "Unverified",
            "confidence": 0.0,
            "reasoning": f"Unable to verify claim due to error: {error}",
            "sources": [],
            "explain_like_12": "We couldn't check this claim because of a technical problem.",
            "harm_score": 0,
            "recommended_action": "monitor",
            "expert_explanation": f"Error during verification: {error}",
            "tags": ["error", "unverified"]
        }
    
    async def generate_explain_like_12(
        self,
        claim_text: str,
        verdict: str,
        reasoning: str
    ) -> str:
        """Generate child-friendly explanation"""
        try:
            prompt = f"""Explain this fact-check result to a 12-year-old:

CLAIM: {claim_text}
VERDICT: {verdict}
WHY: {reasoning[:500]}

Write a simple explanation (50-150 words):
- Use simple words
- Short sentences
- No jargon
- Make it relatable

Explanation:"""
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You explain complex topics simply to children."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=300
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Explain-like-12 generation failed: {e}")
            return "We checked this claim and found it to be " + verdict.lower() + "."
