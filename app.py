import streamlit as st
import sys
import os

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from search import InterviewSearch
from embedder import EmbeddingManager

st.set_page_config(
    page_title="AI Interview Prep Bot",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 AI Interview Prep Bot")
st.markdown("Practice interview questions with AI-powered feedback and suggestions.")

# Initialize components
@st.cache_resource
def initialize_components():
    embedder = EmbeddingManager()
    search_engine = InterviewSearch(embedder)
    return embedder, search_engine

try:
    embedder, search_engine = initialize_components()
except Exception as e:
    st.error(f"Error initializing components: {e}")
    st.stop()

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.selectbox("Choose a page", ["Practice", "Question Bank", "Progress"])

if page == "Practice":
    st.header("🎯 Practice Mode")
    
    # Difficulty selection
    difficulty = st.selectbox("Select difficulty level", ["Easy", "Medium", "Hard"])
    
    # Topic selection
    topics = ["Technical", "Behavioral", "System Design", "Problem Solving", "General"]
    selected_topic = st.selectbox("Select topic", topics)
    
    # Get question
    if st.button("Get Question"):
        with st.spinner("Finding relevant question..."):
            question = search_engine.get_random_question(difficulty, selected_topic)
            if question:
                st.session_state.current_question = question
                st.session_state.user_answer = ""
                st.session_state.show_feedback = False
    
    # Display question and answer interface
    if "current_question" in st.session_state:
        st.subheader("Question:")
        st.write(st.session_state.current_question["question"])
        
        # Answer input
        user_answer = st.text_area(
            "Your Answer:",
            value=st.session_state.get("user_answer", ""),
            height=150
        )
        
        # Submit answer
        if st.button("Submit Answer"):
            if user_answer.strip():
                st.session_state.user_answer = user_answer
                with st.spinner("Analyzing your answer..."):
                    feedback = search_engine.analyze_answer(
                        st.session_state.current_question,
                        user_answer
                    )
                    st.session_state.feedback = feedback
                    st.session_state.show_feedback = True
            else:
                st.warning("Please provide an answer before submitting.")
        
        # Show feedback
        if st.session_state.get("show_feedback", False):
            st.subheader("📝 Feedback")
            feedback = st.session_state.feedback
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Score", f"{feedback.get('score', 0)}/100")
                st.metric("Clarity", f"{feedback.get('clarity', 0)}/10")
            
            with col2:
                st.metric("Relevance", f"{feedback.get('relevance', 0)}/10")
                st.metric("Completeness", f"{feedback.get('completeness', 0)}/10")
            
            st.write("**Detailed Feedback:**")
            st.write(feedback.get("detailed_feedback", "No feedback available."))
            
            st.write("**Sample Answer:**")
            st.info(st.session_state.current_question.get("sample_answer", "No sample answer available."))

elif page == "Question Bank":
    st.header("📚 Question Bank")
    
    # Filters
    col1, col2 = st.columns(2)
    with col1:
        filter_difficulty = st.selectbox("Filter by difficulty", ["All", "Easy", "Medium", "Hard"])
    with col2:
        filter_topic = st.selectbox("Filter by topic", ["All"] + topics)
    
    # Search
    search_query = st.text_input("Search questions...")
    
    # Get filtered questions
    if st.button("Search Questions") or search_query:
        with st.spinner("Searching questions..."):
            questions = search_engine.search_questions(
                query=search_query,
                difficulty=filter_difficulty if filter_difficulty != "All" else None,
                topic=filter_topic if filter_topic != "All" else None
            )
            
            if questions:
                st.write(f"Found {len(questions)} questions:")
                for i, q in enumerate(questions, 1):
                    with st.expander(f"Q{i}: {q['question'][:100]}..."):
                        st.write("**Full Question:**")
                        st.write(q["question"])
                        st.write("**Difficulty:**", q["difficulty"])
                        st.write("**Topic:**", q["topic"])
                        st.write("**Sample Answer:**")
                        st.info(q.get("sample_answer", "No sample answer available."))
            else:
                st.info("No questions found matching your criteria.")

elif page == "Progress":
    st.header("📊 Progress Tracking")
    
    # This would typically track user progress over time
    st.info("Progress tracking feature coming soon! This will show your improvement over time, weak areas, and recommendations.")

# Footer
st.markdown("---")
st.markdown("💡 **Tip:** Practice regularly and focus on areas where you need improvement!")