"""
Embedding and FAISS Vector Search Service
Handles embedding generation and similarity search for claim clustering
"""

import os
import pickle
from typing import List, Dict, Any, Optional
import numpy as np
import faiss
from openai import AsyncOpenAI
from loguru import logger


class EmbeddingService:
    """Service for generating embeddings and vector similarity search"""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.embedding_model = os.getenv("EMBEDDING_MODEL", "text-embedding-3-large")
        self.dimension = 3072  # text-embedding-3-large dimension
        self.index_path = "/app/data/faiss/claims_index.faiss"
        self.metadata_path = "/app/data/faiss/claims_metadata.pkl"
        
        # Initialize FAISS index
        self.index: Optional[faiss.IndexFlatL2] = None
        self.metadata: List[Dict[str, Any]] = []
        
        self._load_or_create_index()
    
    def _load_or_create_index(self):
        """Load existing index or create new one"""
        try:
            if os.path.exists(self.index_path) and os.path.exists(self.metadata_path):
                self.index = faiss.read_index(self.index_path)
                with open(self.metadata_path, 'rb') as f:
                    self.metadata = pickle.load(f)
                logger.info(f"✅ Loaded FAISS index with {self.index.ntotal} vectors")
            else:
                self.index = faiss.IndexFlatL2(self.dimension)
                self.metadata = []
                logger.info("✅ Created new FAISS index")
        except Exception as e:
            logger.error(f"❌ Failed to load/create index: {e}")
            self.index = faiss.IndexFlatL2(self.dimension)
            self.metadata = []
    
    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for text
        
        Args:
            text: Input text
            
        Returns:
            Embedding vector
        """
        try:
            response = await self.client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            
            embedding = response.data[0].embedding
            return embedding
            
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            # Return zero vector as fallback
            return [0.0] * self.dimension
    
    async def add_claim_to_index(
        self,
        claim_id: str,
        claim_text: str,
        embedding: Optional[List[float]] = None
    ):
        """
        Add claim to FAISS index
        
        Args:
            claim_id: Unique claim ID
            claim_text: Claim text
            embedding: Pre-computed embedding (optional)
        """
        try:
            # Generate embedding if not provided
            if embedding is None:
                embedding = await self.generate_embedding(claim_text)
            
            # Convert to numpy array
            vector = np.array([embedding], dtype=np.float32)
            
            # Add to index
            self.index.add(vector)
            
            # Store metadata
            self.metadata.append({
                "claim_id": claim_id,
                "claim_text": claim_text,
                "index_position": self.index.ntotal - 1
            })
            
            # Save index
            self._save_index()
            
            logger.info(f"Added claim {claim_id} to FAISS index (total: {self.index.ntotal})")
            
        except Exception as e:
            logger.error(f"Failed to add claim to index: {e}")
    
    async def find_similar_claims(
        self,
        claim_text: str,
        k: int = 10,
        threshold: float = 0.85
    ) -> List[Dict[str, Any]]:
        """
        Find similar claims using vector similarity
        
        Args:
            claim_text: Query claim
            k: Number of results
            threshold: Similarity threshold (0-1)
            
        Returns:
            List of similar claims with scores
        """
        try:
            if self.index.ntotal == 0:
                return []
            
            # Generate query embedding
            query_embedding = await self.generate_embedding(claim_text)
            query_vector = np.array([query_embedding], dtype=np.float32)
            
            # Search
            distances, indices = self.index.search(query_vector, min(k, self.index.ntotal))
            
            # Convert L2 distances to similarity scores (0-1)
            # similarity = 1 / (1 + distance)
            similarities = 1 / (1 + distances[0])
            
            # Filter by threshold and format results
            results = []
            for idx, similarity in zip(indices[0], similarities):
                if idx < len(self.metadata) and similarity >= threshold:
                    metadata = self.metadata[idx]
                    results.append({
                        "claim_id": metadata["claim_id"],
                        "claim_text": metadata["claim_text"],
                        "similarity_score": float(similarity)
                    })
            
            logger.info(f"Found {len(results)} similar claims above threshold {threshold}")
            return results
            
        except Exception as e:
            logger.error(f"Similarity search failed: {e}")
            return []
    
    def _save_index(self):
        """Save FAISS index and metadata to disk"""
        try:
            os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
            faiss.write_index(self.index, self.index_path)
            
            with open(self.metadata_path, 'wb') as f:
                pickle.dump(self.metadata, f)
            
        except Exception as e:
            logger.error(f"Failed to save index: {e}")
    
    def get_index_stats(self) -> Dict[str, Any]:
        """Get index statistics"""
        return {
            "total_vectors": self.index.ntotal if self.index else 0,
            "dimension": self.dimension,
            "index_type": "FlatL2"
        }
