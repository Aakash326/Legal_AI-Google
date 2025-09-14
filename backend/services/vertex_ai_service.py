import os
from typing import List, Dict, Any, Optional
import logging
from google.cloud import aiplatform
from google.cloud.aiplatform import gapic
import numpy as np

logger = logging.getLogger(__name__)

class VertexAIService:
    def __init__(self, project_id: Optional[str] = None, location: str = "us-central1"):
        self.project_id = project_id or os.getenv("GOOGLE_CLOUD_PROJECT")
        self.location = location
        
        if not self.project_id:
            logger.warning("Google Cloud Project ID not set. Vertex AI features will be limited.")
            return
        
        try:
            # Initialize Vertex AI
            aiplatform.init(project=self.project_id, location=self.location)
            
            # Initialize the prediction client
            client_options = {"api_endpoint": f"{self.location}-aiplatform.googleapis.com"}
            self.prediction_client = gapic.PredictionServiceClient(client_options=client_options)
            
            logger.info(f"Vertex AI initialized for project {self.project_id} in {self.location}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Vertex AI: {str(e)}")
            self.prediction_client = None
    
    def generate_embeddings(self, texts: List[str], model_name: str = "textembedding-gecko@001") -> List[List[float]]:
        """Generate embeddings for text using Vertex AI"""
        if not self.prediction_client:
            logger.warning("Vertex AI not available, returning empty embeddings")
            return [[] for _ in texts]
        
        try:
            # Prepare the endpoint
            endpoint = f"projects/{self.project_id}/locations/{self.location}/publishers/google/models/{model_name}"
            
            embeddings = []
            
            # Process texts in batches to avoid API limits
            batch_size = 5
            for i in range(0, len(texts), batch_size):
                batch_texts = texts[i:i + batch_size]
                
                # Prepare instances for the batch
                instances = [{"content": text} for text in batch_texts]
                
                # Make the prediction request
                response = self.prediction_client.predict(
                    endpoint=endpoint,
                    instances=instances
                )
                
                # Extract embeddings from response
                for prediction in response.predictions:
                    if "embeddings" in prediction:
                        embedding = prediction["embeddings"]["values"]
                        embeddings.append(embedding)
                    else:
                        embeddings.append([])
            
            logger.info(f"Generated embeddings for {len(texts)} texts")
            return embeddings
            
        except Exception as e:
            logger.error(f"Embedding generation failed: {str(e)}")
            return [[] for _ in texts]
    
    def find_similar_texts(self, query_embedding: List[float], text_embeddings: List[List[float]], texts: List[str], top_k: int = 5) -> List[Dict[str, Any]]:
        """Find most similar texts based on embedding similarity"""
        if not query_embedding or not text_embeddings:
            return []
        
        try:
            # Calculate cosine similarity
            similarities = []
            query_array = np.array(query_embedding)
            
            for i, embedding in enumerate(text_embeddings):
                if not embedding:  # Skip empty embeddings
                    continue
                
                embedding_array = np.array(embedding)
                
                # Cosine similarity
                similarity = np.dot(query_array, embedding_array) / (
                    np.linalg.norm(query_array) * np.linalg.norm(embedding_array)
                )
                
                similarities.append({
                    "index": i,
                    "similarity": float(similarity),
                    "text": texts[i] if i < len(texts) else ""
                })
            
            # Sort by similarity and return top k
            similarities.sort(key=lambda x: x["similarity"], reverse=True)
            
            return similarities[:top_k]
            
        except Exception as e:
            logger.error(f"Similarity search failed: {str(e)}")
            return []
    
    def semantic_search(self, query: str, document_chunks: List[str], top_k: int = 5) -> List[Dict[str, Any]]:
        """Perform semantic search on document chunks"""
        try:
            # Generate embedding for query
            query_embeddings = self.generate_embeddings([query])
            if not query_embeddings or not query_embeddings[0]:
                logger.warning("Failed to generate query embedding")
                return []
            
            query_embedding = query_embeddings[0]
            
            # Generate embeddings for document chunks
            chunk_embeddings = self.generate_embeddings(document_chunks)
            
            # Find similar chunks
            similar_chunks = self.find_similar_texts(
                query_embedding, chunk_embeddings, document_chunks, top_k
            )
            
            logger.info(f"Semantic search found {len(similar_chunks)} relevant chunks")
            return similar_chunks
            
        except Exception as e:
            logger.error(f"Semantic search failed: {str(e)}")
            return []
    
    def cluster_text_chunks(self, texts: List[str], num_clusters: int = 5) -> Dict[str, Any]:
        """Cluster text chunks based on semantic similarity"""
        try:
            # Generate embeddings for all texts
            embeddings = self.generate_embeddings(texts)
            
            # Filter out empty embeddings
            valid_embeddings = []
            valid_indices = []
            
            for i, embedding in enumerate(embeddings):
                if embedding:
                    valid_embeddings.append(embedding)
                    valid_indices.append(i)
            
            if len(valid_embeddings) < num_clusters:
                logger.warning(f"Not enough valid embeddings for clustering ({len(valid_embeddings)} < {num_clusters})")
                return {"clusters": [], "error": "Insufficient data for clustering"}
            
            # Simple k-means clustering using numpy
            from sklearn.cluster import KMeans
            
            kmeans = KMeans(n_clusters=num_clusters, random_state=42)
            cluster_labels = kmeans.fit_predict(valid_embeddings)
            
            # Organize results by cluster
            clusters = {}
            for i, label in enumerate(cluster_labels):
                original_index = valid_indices[i]
                if label not in clusters:
                    clusters[label] = []
                clusters[label].append({
                    "index": original_index,
                    "text": texts[original_index]
                })
            
            return {
                "clusters": [clusters[i] for i in sorted(clusters.keys())],
                "num_clusters": len(clusters),
                "total_texts": len(valid_embeddings)
            }
            
        except ImportError:
            logger.warning("sklearn not available for clustering")
            return {"clusters": [], "error": "Clustering library not available"}
        except Exception as e:
            logger.error(f"Text clustering failed: {str(e)}")
            return {"clusters": [], "error": str(e)}
    
    def analyze_text_similarity_matrix(self, texts: List[str]) -> Dict[str, Any]:
        """Generate similarity matrix for a list of texts"""
        try:
            embeddings = self.generate_embeddings(texts)
            
            # Filter valid embeddings
            valid_embeddings = [emb for emb in embeddings if emb]
            
            if len(valid_embeddings) < 2:
                return {"similarity_matrix": [], "error": "Need at least 2 valid embeddings"}
            
            # Calculate pairwise similarities
            n = len(valid_embeddings)
            similarity_matrix = [[0.0 for _ in range(n)] for _ in range(n)]
            
            for i in range(n):
                for j in range(n):
                    if i == j:
                        similarity_matrix[i][j] = 1.0
                    else:
                        emb1 = np.array(valid_embeddings[i])
                        emb2 = np.array(valid_embeddings[j])
                        
                        similarity = np.dot(emb1, emb2) / (
                            np.linalg.norm(emb1) * np.linalg.norm(emb2)
                        )
                        similarity_matrix[i][j] = float(similarity)
            
            return {
                "similarity_matrix": similarity_matrix,
                "text_count": n,
                "average_similarity": np.mean([similarity_matrix[i][j] for i in range(n) for j in range(n) if i != j])
            }
            
        except Exception as e:
            logger.error(f"Similarity matrix analysis failed: {str(e)}")
            return {"similarity_matrix": [], "error": str(e)}
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get status of Vertex AI service"""
        return {
            "available": self.prediction_client is not None,
            "project_id": self.project_id,
            "location": self.location,
            "initialized": hasattr(self, 'prediction_client') and self.prediction_client is not None
        }

# Global instance
vertex_ai_service = None

def get_vertex_ai_service() -> VertexAIService:
    """Get global Vertex AI service instance"""
    global vertex_ai_service
    if vertex_ai_service is None:
        vertex_ai_service = VertexAIService()
    return vertex_ai_service