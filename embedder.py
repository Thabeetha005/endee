import json
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import pickle
from typing import List, Dict, Any
import os

class EmbeddingManager:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the embedding manager with a sentence transformer model.
        
        Args:
            model_name: Name of the sentence transformer model to use
        """
        self.model_name = model_name
        self.model = None
        self.index = None
        self.questions_data = []
        self.embeddings = None
        
        # Load model and data
        self._load_model()
        self._load_or_create_embeddings()
    
    def _load_model(self):
        """Load the sentence transformer model."""
        try:
            self.model = SentenceTransformer(self.model_name)
            print(f"Loaded model: {self.model_name}")
        except Exception as e:
            print(f"Error loading model: {e}")
            raise
    
    def _load_or_create_embeddings(self):
        """Load existing embeddings or create new ones from the dataset."""
        embedding_file = "embeddings/faiss_index.pkl"
        data_file = "dataset/interview_qa.json"
        
        # Check if files exist
        if os.path.exists(embedding_file) and os.path.exists(data_file):
            try:
                self._load_embeddings(embedding_file)
                self._load_questions_data(data_file)
                print("Loaded existing embeddings and data")
                return
            except Exception as e:
                print(f"Error loading existing files: {e}")
        
        # Create new embeddings
        if os.path.exists(data_file):
            self._load_questions_data(data_file)
            self._create_embeddings()
            self._save_embeddings(embedding_file)
        else:
            print(f"Data file {data_file} not found")
    
    def _load_questions_data(self, data_file: str):
        """Load questions from the JSON dataset."""
        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                self.questions_data = json.load(f)
            print(f"Loaded {len(self.questions_data)} questions")
        except Exception as e:
            print(f"Error loading questions data: {e}")
            self.questions_data = []
    
    def _create_embeddings(self):
        """Create embeddings for all questions."""
        if not self.questions_data:
            print("No questions data available")
            return
        
        # Prepare texts for embedding (question + context)
        texts = []
        for q in self.questions_data:
            # Combine question with topic and difficulty for better semantic search
            text = f"{q['question']} {q.get('topic', '')} {q.get('difficulty', '')}"
            texts.append(text)
        
        # Create embeddings
        print("Creating embeddings...")
        self.embeddings = self.model.encode(texts, show_progress_bar=True)
        
        # Create FAISS index
        dimension = self.embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
        
        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(self.embeddings)
        self.index.add(self.embeddings)
        
        print(f"Created FAISS index with {len(self.embeddings)} embeddings")
    
    def _save_embeddings(self, embedding_file: str):
        """Save embeddings and index to disk."""
        try:
            os.makedirs(os.path.dirname(embedding_file), exist_ok=True)
            
            # Save FAISS index and metadata
            save_data = {
                'index': self.index,
                'embeddings': self.embeddings,
                'questions_data': self.questions_data,
                'model_name': self.model_name
            }
            
            with open(embedding_file, 'wb') as f:
                pickle.dump(save_data, f)
            
            print(f"Saved embeddings to {embedding_file}")
        except Exception as e:
            print(f"Error saving embeddings: {e}")
    
    def _load_embeddings(self, embedding_file: str):
        """Load embeddings and index from disk."""
        try:
            with open(embedding_file, 'rb') as f:
                save_data = pickle.load(f)
            
            self.index = save_data['index']
            self.embeddings = save_data['embeddings']
            self.questions_data = save_data['questions_data']
            
            print(f"Loaded embeddings from {embedding_file}")
        except Exception as e:
            print(f"Error loading embeddings: {e}")
            raise
    
    def search_similar_questions(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar questions using semantic similarity.
        
        Args:
            query: Search query
            k: Number of results to return
            
        Returns:
            List of similar questions with similarity scores
        """
        if not self.index or not self.model:
            return []
        
        # Create query embedding
        query_embedding = self.model.encode([query])
        faiss.normalize_L2(query_embedding)
        
        # Search
        scores, indices = self.index.search(query_embedding, k)
        
        # Prepare results
        results = []
        for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
            if idx < len(self.questions_data):
                question_data = self.questions_data[idx].copy()
                question_data['similarity_score'] = float(score)
                results.append(question_data)
        
        return results
    
    def get_embedding(self, text: str) -> np.ndarray:
        """
        Get embedding for a single text.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        if not self.model:
            raise ValueError("Model not loaded")
        
        embedding = self.model.encode([text])[0]
        return embedding
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate cosine similarity between two texts.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Cosine similarity score
        """
        emb1 = self.get_embedding(text1)
        emb2 = self.get_embedding(text2)
        
        # Normalize embeddings
        emb1_norm = emb1 / np.linalg.norm(emb1)
        emb2_norm = emb2 / np.linalg.norm(emb2)
        
        # Calculate cosine similarity
        similarity = np.dot(emb1_norm, emb2_norm)
        return float(similarity)
    
    def add_questions(self, new_questions: List[Dict[str, Any]]):
        """
        Add new questions to the existing dataset.
        
        Args:
            new_questions: List of new question dictionaries
        """
        if not new_questions:
            return
        
        # Add to existing data
        self.questions_data.extend(new_questions)
        
        # Recreate embeddings
        self._create_embeddings()
        
        # Save updated embeddings
        self._save_embeddings("embeddings/faiss_index.pkl")
        
        print(f"Added {len(new_questions)} new questions")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the embedded dataset.
        
        Returns:
            Dictionary with dataset statistics
        """
        if not self.questions_data:
            return {"total_questions": 0}
        
        # Count by difficulty
        difficulty_counts = {}
        topic_counts = {}
        
        for q in self.questions_data:
            diff = q.get('difficulty', 'Unknown')
            topic = q.get('topic', 'Unknown')
            
            difficulty_counts[diff] = difficulty_counts.get(diff, 0) + 1
            topic_counts[topic] = topic_counts.get(topic, 0) + 1
        
        return {
            "total_questions": len(self.questions_data),
            "difficulty_distribution": difficulty_counts,
            "topic_distribution": topic_counts,
            "model_name": self.model_name,
            "embedding_dimension": self.embeddings.shape[1] if self.embeddings is not None else 0
        }