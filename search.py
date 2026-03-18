import random
import json
from typing import List, Dict, Any, Optional
from embedder import EmbeddingManager
import re

class InterviewSearch:
    def __init__(self, embedder: EmbeddingManager):
        """
        Initialize the interview search engine.
        
        Args:
            embedder: EmbeddingManager instance for semantic search
        """
        self.embedder = embedder
    
    def get_random_question(self, difficulty: str = None, topic: str = None) -> Optional[Dict[str, Any]]:
        """
        Get a random question, optionally filtered by difficulty and topic.
        
        Args:
            difficulty: Filter by difficulty level
            topic: Filter by topic
            
        Returns:
            Random question dictionary or None if no questions found
        """
        questions = self.embedder.questions_data
        
        # Apply filters
        if difficulty:
            questions = [q for q in questions if q.get('difficulty') == difficulty]
        
        if topic:
            questions = [q for q in questions if q.get('topic') == topic]
        
        if not questions:
            return None
        
        return random.choice(questions)
    
    def search_questions(self, query: str = "", difficulty: str = None, topic: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for questions based on query text and filters.
        
        Args:
            query: Search query for semantic search
            difficulty: Filter by difficulty level
            topic: Filter by topic
            limit: Maximum number of results to return
            
        Returns:
            List of matching questions
        """
        questions = self.embedder.questions_data
        
        # Apply filters
        if difficulty:
            questions = [q for q in questions if q.get('difficulty') == difficulty]
        
        if topic:
            questions = [q for q in questions if q.get('topic') == topic]
        
        # If there's a query, use semantic search
        if query and query.strip():
            semantic_results = self.embedder.search_similar_questions(query, k=limit)
            
            # Filter semantic results by difficulty/topic if specified
            if difficulty or topic:
                filtered_results = []
                for result in semantic_results:
                    if difficulty and result.get('difficulty') != difficulty:
                        continue
                    if topic and result.get('topic') != topic:
                        continue
                    filtered_results.append(result)
                return filtered_results[:limit]
            
            return semantic_results[:limit]
        
        # If no query, return filtered questions randomly
        if questions:
            return random.sample(questions, min(len(questions), limit))
        
        return []
    
    def analyze_answer(self, question: Dict[str, Any], user_answer: str) -> Dict[str, Any]:
        """
        Analyze the user's answer and provide feedback.
        
        Args:
            question: Question dictionary with sample answer
            user_answer: User's answer text
            
        Returns:
            Dictionary with analysis results and feedback
        """
        sample_answer = question.get('sample_answer', '')
        
        if not sample_answer:
            return {
                'score': 50,
                'clarity': 5,
                'relevance': 5,
                'completeness': 5,
                'detailed_feedback': 'No sample answer available for comparison. Please consult with a mentor for feedback.'
            }
        
        # Calculate semantic similarity
        similarity_score = self.embedder.calculate_similarity(user_answer, sample_answer)
        
        # Analyze various aspects
        clarity_score = self._analyze_clarity(user_answer)
        relevance_score = self._analyze_relevance(user_answer, question)
        completeness_score = self._analyze_completeness(user_answer, sample_answer)
        
        # Calculate overall score
        overall_score = (similarity_score * 40 + clarity_score * 20 + relevance_score * 20 + completeness_score * 20) / 100
        
        # Generate detailed feedback
        feedback = self._generate_feedback(user_answer, sample_answer, {
            'similarity': similarity_score,
            'clarity': clarity_score,
            'relevance': relevance_score,
            'completeness': completeness_score
        })
        
        return {
            'score': round(overall_score * 100),
            'clarity': clarity_score,
            'relevance': relevance_score,
            'completeness': completeness_score,
            'detailed_feedback': feedback
        }
    
    def _analyze_clarity(self, answer: str) -> int:
        """
        Analyze the clarity of the answer.
        
        Args:
            answer: User's answer text
            
        Returns:
            Clarity score (1-10)
        """
        score = 5  # Base score
        
        # Check for proper sentence structure
        sentences = re.split(r'[.!?]+', answer)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) >= 3:
            score += 2
        elif len(sentences) >= 2:
            score += 1
        
        # Check for appropriate length
        word_count = len(answer.split())
        if 50 <= word_count <= 300:
            score += 2
        elif word_count >= 30:
            score += 1
        
        # Check for formatting
        if any(char in answer for char in ['-', '*', '1.', '2.']):
            score += 1
        
        # Penalize for very short answers
        if word_count < 20:
            score -= 2
        
        return max(1, min(10, score))
    
    def _analyze_relevance(self, answer: str, question: Dict[str, Any]) -> int:
        """
        Analyze the relevance of the answer to the question.
        
        Args:
            answer: User's answer text
            question: Question dictionary
            
        Returns:
            Relevance score (1-10)
        """
        score = 5  # Base score
        
        question_text = question.get('question', '').lower()
        answer_lower = answer.lower()
        
        # Check if answer addresses the question
        question_words = set(question_text.split())
        answer_words = set(answer_lower.split())
        
        # Calculate word overlap
        overlap = len(question_words.intersection(answer_words))
        if overlap >= 3:
            score += 3
        elif overlap >= 2:
            score += 2
        elif overlap >= 1:
            score += 1
        
        # Check for topic relevance
        topic = question.get('topic', '').lower()
        if topic and topic in answer_lower:
            score += 2
        
        # Penalize for completely unrelated content
        if overlap == 0:
            score -= 3
        
        return max(1, min(10, score))
    
    def _analyze_completeness(self, user_answer: str, sample_answer: str) -> int:
        """
        Analyze the completeness of the user's answer compared to sample answer.
        
        Args:
            user_answer: User's answer text
            sample_answer: Sample answer text
            
        Returns:
            Completeness score (1-10)
        """
        score = 5  # Base score
        
        # Compare length
        user_words = len(user_answer.split())
        sample_words = len(sample_answer.split())
        
        length_ratio = user_words / max(sample_words, 1)
        
        if 0.7 <= length_ratio <= 1.3:
            score += 3
        elif 0.5 <= length_ratio <= 1.5:
            score += 2
        elif 0.3 <= length_ratio <= 2:
            score += 1
        else:
            score -= 1
        
        # Check for key concepts (this is a simplified approach)
        sample_sentences = re.split(r'[.!?]+', sample_answer)
        user_sentences = re.split(r'[.!?]+', user_answer)
        
        # Reward multiple sentences
        if len(user_sentences) >= 3:
            score += 2
        elif len(user_sentences) >= 2:
            score += 1
        
        return max(1, min(10, score))
    
    def _generate_feedback(self, user_answer: str, sample_answer: str, scores: Dict[str, float]) -> str:
        """
        Generate detailed feedback based on analysis.
        
        Args:
            user_answer: User's answer text
            sample_answer: Sample answer text
            scores: Dictionary with various scores
            
        Returns:
            Detailed feedback string
        """
        feedback_parts = []
        
        # Overall assessment
        similarity = scores['similarity']
        if similarity >= 0.8:
            feedback_parts.append("Excellent answer! Your response closely matches the expected answer.")
        elif similarity >= 0.6:
            feedback_parts.append("Good answer! You're on the right track with some room for improvement.")
        elif similarity >= 0.4:
            feedback_parts.append("Fair attempt. Consider including more key concepts and details.")
        else:
            feedback_parts.append("Your answer needs significant improvement. Review the sample answer for guidance.")
        
        # Specific feedback based on scores
        if scores['clarity'] < 6:
            feedback_parts.append("\n\n**Clarity:** Try to structure your answer better with clear sentences and proper formatting.")
        
        if scores['relevance'] < 6:
            feedback_parts.append("\n\n**Relevance:** Make sure your answer directly addresses the question asked.")
        
        if scores['completeness'] < 6:
            feedback_parts.append("\n\n**Completeness:** Consider adding more details and examples to make your answer more comprehensive.")
        
        # Positive reinforcement
        if scores['clarity'] >= 8:
            feedback_parts.append("\n\n**Strength:** Your answer is well-structured and easy to understand.")
        
        if scores['relevance'] >= 8:
            feedback_parts.append("\n\n**Strength:** You've directly addressed the question well.")
        
        return "".join(feedback_parts)
    
    def get_questions_by_topic(self, topic: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get questions by topic.
        
        Args:
            topic: Topic to filter by
            limit: Maximum number of questions to return
            
        Returns:
            List of questions for the specified topic
        """
        questions = [q for q in self.embedder.questions_data if q.get('topic') == topic]
        return random.sample(questions, min(len(questions), limit)) if questions else []
    
    def get_questions_by_difficulty(self, difficulty: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get questions by difficulty level.
        
        Args:
            difficulty: Difficulty level to filter by
            limit: Maximum number of questions to return
            
        Returns:
            List of questions for the specified difficulty
        """
        questions = [q for q in self.embedder.questions_data if q.get('difficulty') == difficulty]
        return random.sample(questions, min(len(questions), limit)) if questions else []
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the question database.
        
        Returns:
            Dictionary with database statistics
        """
        return self.embedder.get_stats()
