"""
Claim Clustering Service
Groups similar claims together and identifies trending topics
"""

import os
from typing import List, Dict, Any
from collections import Counter
from datetime import datetime, timedelta
import hdbscan
import numpy as np
from loguru import logger

from motor.motor_asyncio import AsyncIOMotorDatabase
from .embedding_service import EmbeddingService


class ClusteringService:
    """Service for clustering similar claims"""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        self.db = database
        self.embedding_service = EmbeddingService()
        self.min_cluster_size = int(os.getenv("MIN_CLUSTER_SIZE", "3"))
        self.similarity_threshold = float(os.getenv("SIMILARITY_THRESHOLD", "0.85"))
    
    async def cluster_recent_claims(self, hours: int = 24) -> List[Dict[str, Any]]:
        """
        Cluster claims from the last N hours
        
        Args:
            hours: Time window in hours
            
        Returns:
            List of clusters with metadata
        """
        try:
            # Get recent claims with embeddings
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            claims_cursor = self.db.claims.find({
                "created_at": {"$gte": cutoff_time},
                "embedding": {"$exists": True, "$ne": None}
            })
            
            claims = await claims_cursor.to_list(length=1000)
            
            if len(claims) < self.min_cluster_size:
                logger.info(f"Not enough claims to cluster ({len(claims)} < {self.min_cluster_size})")
                return []
            
            # Extract embeddings and IDs
            embeddings = []
            claim_ids = []
            claim_texts = []
            
            for claim in claims:
                if claim.get("embedding"):
                    embeddings.append(claim["embedding"])
                    claim_ids.append(str(claim["_id"]))
                    claim_texts.append(claim["claim_text"])
            
            # Run clustering
            clusters = await self._run_hdbscan_clustering(embeddings, claim_ids, claim_texts)
            
            # Save clusters to database
            await self._save_clusters(clusters)
            
            logger.info(f"Created {len(clusters)} clusters from {len(claims)} claims")
            return clusters
            
        except Exception as e:
            logger.error(f"Clustering failed: {e}")
            return []
    
    async def _run_hdbscan_clustering(
        self,
        embeddings: List[List[float]],
        claim_ids: List[str],
        claim_texts: List[str]
    ) -> List[Dict[str, Any]]:
        """Run HDBSCAN clustering algorithm"""
        try:
            # Convert to numpy array
            X = np.array(embeddings, dtype=np.float32)
            
            # Run HDBSCAN
            clusterer = hdbscan.HDBSCAN(
                min_cluster_size=self.min_cluster_size,
                metric='euclidean',
                cluster_selection_method='eom'
            )
            
            cluster_labels = clusterer.fit_predict(X)
            
            # Group claims by cluster
            clusters = {}
            for claim_id, claim_text, label in zip(claim_ids, claim_texts, cluster_labels):
                if label == -1:  # Noise point
                    continue
                
                if label not in clusters:
                    clusters[label] = {
                        "claim_ids": [],
                        "claim_texts": []
                    }
                
                clusters[label]["claim_ids"].append(claim_id)
                clusters[label]["claim_texts"].append(claim_text)
            
            # Format clusters
            formatted_clusters = []
            for cluster_id, data in clusters.items():
                cluster = await self._format_cluster(cluster_id, data)
                formatted_clusters.append(cluster)
            
            return formatted_clusters
            
        except Exception as e:
            logger.error(f"HDBSCAN clustering failed: {e}")
            return []
    
    async def _format_cluster(self, cluster_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format cluster with metadata"""
        claim_texts = data["claim_texts"]
        claim_ids = data["claim_ids"]
        
        # Generate cluster label (using most common words or AI)
        label = self._generate_cluster_label(claim_texts)
        
        # Select representative claim (longest or most central)
        representative = max(claim_texts, key=len)
        
        # Calculate trend score based on recency and volume
        trend_score = min(100.0, len(claim_ids) * 10)
        
        return {
            "cluster_id": f"cluster_{cluster_id}_{int(datetime.utcnow().timestamp())}",
            "label": label,
            "claim_ids": claim_ids,
            "representative_claim": representative,
            "claim_count": len(claim_ids),
            "is_trending": len(claim_ids) >= 5,
            "trend_score": trend_score,
            "category": "general"  # Could be enhanced with classification
        }
    
    def _generate_cluster_label(self, claim_texts: List[str]) -> str:
        """Generate a label for the cluster"""
        # Simple word frequency approach
        # In production, use LLM for better labels
        
        all_words = []
        for text in claim_texts:
            words = text.lower().split()
            # Filter out common words
            filtered = [w for w in words if len(w) > 4 and w not in 
                       ['about', 'there', 'their', 'would', 'could', 'should']]
            all_words.extend(filtered[:5])
        
        if not all_words:
            return "Unnamed Cluster"
        
        # Get most common words
        word_counts = Counter(all_words)
        top_words = [word for word, count in word_counts.most_common(3)]
        
        return " ".join(top_words).title()
    
    async def _save_clusters(self, clusters: List[Dict[str, Any]]):
        """Save clusters to database"""
        try:
            for cluster in clusters:
                cluster["created_at"] = datetime.utcnow()
                cluster["last_updated"] = datetime.utcnow()
                
                # Upsert cluster
                await self.db.clusters.update_one(
                    {"cluster_id": cluster["cluster_id"]},
                    {"$set": cluster},
                    upsert=True
                )
                
                # Update claims with cluster_id
                await self.db.claims.update_many(
                    {"_id": {"$in": cluster["claim_ids"]}},
                    {"$set": {"cluster_id": cluster["cluster_id"]}}
                )
            
            logger.info(f"Saved {len(clusters)} clusters to database")
            
        except Exception as e:
            logger.error(f"Failed to save clusters: {e}")
    
    async def get_trending_clusters(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get trending clusters"""
        try:
            cursor = self.db.clusters.find(
                {"is_trending": True}
            ).sort("trend_score", -1).limit(limit)
            
            clusters = await cursor.to_list(length=limit)
            
            # Convert ObjectId to string
            for cluster in clusters:
                cluster["id"] = str(cluster.pop("_id"))
            
            return clusters
            
        except Exception as e:
            logger.error(f"Failed to get trending clusters: {e}")
            return []
