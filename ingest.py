import json
import os
from typing import List, Dict, Any
from embedder import EmbeddingManager

class DataIngestion:
    def __init__(self, embedder: EmbeddingManager):
        """
        Initialize the data ingestion system.
        
        Args:
            embedder: EmbeddingManager instance
        """
        self.embedder = embedder
    
    def load_from_json(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Load interview questions from a JSON file.
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            List of question dictionaries
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Validate data structure
            if not isinstance(data, list):
                raise ValueError("JSON file should contain a list of questions")
            
            validated_questions = []
            for i, item in enumerate(data):
                if self._validate_question(item, i):
                    validated_questions.append(item)
            
            print(f"Loaded and validated {len(validated_questions)} questions from {file_path}")
            return validated_questions
            
        except Exception as e:
            print(f"Error loading JSON file: {e}")
            return []
    
    def _validate_question(self, question: Dict[str, Any], index: int) -> bool:
        """
        Validate a single question dictionary.
        
        Args:
            question: Question dictionary to validate
            index: Index of the question in the list
            
        Returns:
            True if valid, False otherwise
        """
        required_fields = ['question', 'difficulty', 'topic']
        
        # Check required fields
        for field in required_fields:
            if field not in question:
                print(f"Question {index}: Missing required field '{field}'")
                return False
        
        # Validate field types
        if not isinstance(question['question'], str) or not question['question'].strip():
            print(f"Question {index}: Invalid question text")
            return False
        
        if question['difficulty'] not in ['Easy', 'Medium', 'Hard']:
            print(f"Question {index}: Invalid difficulty level. Must be 'Easy', 'Medium', or 'Hard'")
            return False
        
        if not isinstance(question['topic'], str) or not question['topic'].strip():
            print(f"Question {index}: Invalid topic")
            return False
        
        # Optional field validation
        if 'sample_answer' in question:
            if not isinstance(question['sample_answer'], str):
                print(f"Question {index}: Invalid sample_answer type")
                return False
        
        return True
    
    def add_questions(self, questions: List[Dict[str, Any]]) -> int:
        """
        Add new questions to the embedding system.
        
        Args:
            questions: List of question dictionaries
            
        Returns:
            Number of questions successfully added
        """
        if not questions:
            return 0
        
        # Validate all questions
        valid_questions = []
        for i, question in enumerate(questions):
            if self._validate_question(question, i):
                valid_questions.append(question)
        
        if not valid_questions:
            print("No valid questions to add")
            return 0
        
        # Add to embedder
        self.embedder.add_questions(valid_questions)
        
        return len(valid_questions)
    
    def get_import_stats(self) -> Dict[str, Any]:
        """
        Get statistics about imported questions.
        
        Returns:
            Dictionary with import statistics
        """
        return self.embedder.get_stats()

# Main execution function
def main():
    """
    Main function to run data ingestion.
    """
    print("Starting data ingestion...")
    
    # Initialize embedder
    embedder = EmbeddingManager()
    
    # Initialize ingestion
    ingestion = DataIngestion(embedder)
    
    # Load and ingest data
    questions = ingestion.load_from_json("dataset/interview_qa.json")
    if questions:
        added_count = ingestion.add_questions(questions)
        print(f"Successfully added {added_count} questions to the system")
    
    # Print stats
    stats = ingestion.get_import_stats()
    print("\nDatabase Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")

if __name__ == "__main__":
    main()