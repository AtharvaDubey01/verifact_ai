"""
Evidence Retrieval Agent
Retrieves evidence from multiple sources
"""

import os
import asyncio
from typing import List, Dict, Any
from datetime import datetime
import httpx
import feedparser
from bs4 import BeautifulSoup
from loguru import logger
from urllib.parse import urlparse


class EvidenceRetrieverAgent:
    """AI Agent for retrieving evidence from multiple sources"""
    
    def __init__(self):
        self.news_api_key = os.getenv("NEWS_API_KEY")
        self.google_factcheck_key = os.getenv("GOOGLE_FACTCHECK_API_KEY")
        self.timeout = 10
        self.max_sources = 10
    
    async def retrieve_evidence(
        self,
        claim_text: str,
        entities: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Retrieve evidence from multiple sources
        
        Args:
            claim_text: The claim to verify
            entities: Extracted entities to help with search
            
        Returns:
            Dictionary containing evidence sources
        """
        try:
            # Generate search queries
            search_queries = self._generate_search_queries(claim_text, entities or [])
            
            # Retrieve from multiple sources in parallel
            tasks = [
                self._search_google_factcheck(search_queries[0] if search_queries else claim_text),
                self._search_news_api(claim_text),
                self._search_web_general(claim_text),
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Combine and deduplicate sources
            all_sources = []
            for result in results:
                if isinstance(result, list):
                    all_sources.extend(result)
            
            # Remove duplicates based on URL
            unique_sources = self._deduplicate_sources(all_sources)
            
            # Score and rank sources
            ranked_sources = self._rank_sources(unique_sources)
            
            # Limit to top sources
            top_sources = ranked_sources[:self.max_sources]
            
            logger.info(f"Retrieved {len(top_sources)} evidence sources for claim")
            
            return {
                "sources": top_sources,
                "total_sources_found": len(all_sources),
                "search_queries": search_queries,
                "retrieval_method": "multi-source"
            }
            
        except Exception as e:
            logger.error(f"Evidence retrieval failed: {e}")
            return {
                "sources": [],
                "total_sources_found": 0,
                "search_queries": [],
                "error": str(e)
            }
    
    def _generate_search_queries(self, claim_text: str, entities: List[Dict]) -> List[str]:
        """Generate effective search queries"""
        queries = [claim_text]
        
        # Add entity-based queries
        entity_texts = [e.get("text", "") for e in entities if e.get("text")]
        if entity_texts:
            entity_query = " ".join(entity_texts[:3])
            queries.append(f"{entity_query} fact check")
        
        # Add fact-check specific query
        queries.append(f'"{claim_text}" fact check')
        
        return queries[:5]
    
    async def _search_google_factcheck(self, query: str) -> List[Dict[str, Any]]:
        """Search Google Fact Check API"""
        if not self.google_factcheck_key:
            logger.warning("Google Fact Check API key not configured")
            return []
        
        try:
            url = "https://factchecktools.googleapis.com/v1alpha1/claims:search"
            params = {
                "query": query,
                "key": self.google_factcheck_key,
                "languageCode": "en"
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
            
            sources = []
            for claim in data.get("claims", [])[:5]:
                for review in claim.get("claimReview", []):
                    sources.append({
                        "url": review.get("url", ""),
                        "title": review.get("title", "Fact Check"),
                        "excerpt": claim.get("text", "")[:500],
                        "published_date": review.get("reviewDate"),
                        "domain": urlparse(review.get("url", "")).netloc,
                        "reliability_score": 0.9,  # Fact-check sites are reliable
                        "source_type": "fact-check"
                    })
            
            logger.info(f"Google Fact Check: found {len(sources)} sources")
            return sources
            
        except Exception as e:
            logger.error(f"Google Fact Check search failed: {e}")
            return []
    
    async def _search_news_api(self, query: str) -> List[Dict[str, Any]]:
        """Search NewsAPI"""
        if not self.news_api_key:
            logger.warning("NewsAPI key not configured")
            return []
        
        try:
            url = "https://newsapi.org/v2/everything"
            params = {
                "q": query,
                "apiKey": self.news_api_key,
                "language": "en",
                "sortBy": "relevancy",
                "pageSize": 10
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
            
            sources = []
            for article in data.get("articles", []):
                sources.append({
                    "url": article.get("url", ""),
                    "title": article.get("title", ""),
                    "excerpt": article.get("description", "")[:500],
                    "published_date": article.get("publishedAt"),
                    "domain": urlparse(article.get("url", "")).netloc,
                    "reliability_score": self._estimate_domain_reliability(
                        urlparse(article.get("url", "")).netloc
                    ),
                    "source_type": "article"
                })
            
            logger.info(f"NewsAPI: found {len(sources)} sources")
            return sources
            
        except Exception as e:
            logger.error(f"NewsAPI search failed: {e}")
            return []
    
    async def _search_web_general(self, query: str) -> List[Dict[str, Any]]:
        """Search general web sources (fallback)"""
        # This is a placeholder for additional sources like:
        # - Wikipedia API
        # - Government health sites (CDC, WHO)
        # - Academic databases
        # For hackathon purposes, return empty
        return []
    
    def _deduplicate_sources(self, sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate sources based on URL"""
        seen_urls = set()
        unique = []
        
        for source in sources:
            url = source.get("url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique.append(source)
        
        return unique
    
    def _rank_sources(self, sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Rank sources by reliability and relevance"""
        # Sort by reliability score (descending)
        return sorted(sources, key=lambda x: x.get("reliability_score", 0.0), reverse=True)
    
    def _estimate_domain_reliability(self, domain: str) -> float:
        """Estimate reliability of a domain"""
        # High reliability domains
        high_reliability = [
            "who.int", "cdc.gov", "nih.gov", "nature.com", "science.org",
            "reuters.com", "apnews.com", "bbc.com", "npr.org",
            "snopes.com", "factcheck.org", "politifact.com"
        ]
        
        # Medium reliability
        medium_reliability = [
            "nytimes.com", "washingtonpost.com", "theguardian.com",
            "cnn.com", "abcnews.go.com", "cbsnews.com"
        ]
        
        domain_lower = domain.lower()
        
        if any(d in domain_lower for d in high_reliability):
            return 0.95
        elif any(d in domain_lower for d in medium_reliability):
            return 0.75
        elif domain.endswith(".gov") or domain.endswith(".edu"):
            return 0.85
        else:
            return 0.5  # Default medium reliability
    
    async def fetch_url_content(self, url: str) -> str:
        """Fetch and extract text content from URL"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'lxml')
                
                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.decompose()
                
                # Get text
                text = soup.get_text()
                
                # Clean up whitespace
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                text = ' '.join(chunk for chunk in chunks if chunk)
                
                return text[:5000]  # Limit length
                
        except Exception as e:
            logger.error(f"Failed to fetch {url}: {e}")
            return ""
