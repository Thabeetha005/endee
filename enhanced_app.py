import streamlit as st
import sys
import os
import json
import random

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

st.set_page_config(
    page_title="AI Interview Prep Bot",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 AI Interview Prep Bot")
st.markdown("Practice interview questions with AI-powered feedback.")

# Load interview questions dataset
@st.cache_data
def load_questions():
    try:
        with open('dataset/interview_qa.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error loading questions: {e}")
        return []

# Initialize questions
questions = load_questions()

if questions:
    st.success(f"✅ Loaded {len(questions)} interview questions!")
    
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Choose a page", ["Practice", "Question Bank", "Progress"])
    
    if page == "Practice":
        st.header("🎯 Practice Mode")
        
        # Difficulty selection
        difficulty = st.selectbox("Select difficulty level", ["Easy", "Medium", "Hard"])
        
        # Topic selection
        topics = list(set([q.get('topic') for q in questions]))
        selected_topic = st.selectbox("Select topic", topics)
        
        # Get question
        if st.button("Get Question"):
            # Filter questions
            filtered_questions = questions.copy()
            if difficulty != "Easy":
                filtered_questions = [q for q in filtered_questions if q.get('difficulty') == difficulty]
            if selected_topic != topics[0]:  # Don't filter if "All"
                filtered_questions = [q for q in filtered_questions if q.get('topic') == selected_topic]
            
            if filtered_questions:
                question = random.choice(filtered_questions)
                st.session_state.current_question = question
                st.session_state.user_answer = ""
                st.session_state.show_feedback = False
        
        # Display question and answer interface
        if "current_question" in st.session_state:
            st.subheader("Question:")
            st.write(st.session_state.current_question["question"])
            
            # Display sample answer for reference
            with st.expander("💡 Sample Answer (for reference)"):
                st.info(st.session_state.current_question.get("sample_answer", "No sample answer available."))
            
            # Answer input
            user_answer = st.text_area(
                "Your Answer:",
                value=st.session_state.get("user_answer", ""),
                height=150,
                placeholder="Type your answer here..."
            )
            
            # Submit answer
            if st.button("Submit Answer", key="submit_answer"):
                if user_answer.strip():
                    st.session_state.user_answer = user_answer
                    st.session_state.show_feedback = True
                    
                    # Enhanced feedback analysis
                    similarity = len(set(user_answer.lower().split()) & set(st.session_state.current_question.get("sample_answer", "").lower().split())) / len(set(st.session_state.current_question.get("sample_answer", "").lower().split())) * 100
                    
                    # Multi-dimensional scoring
                    clarity_score = min(10, max(1, len(user_answer.split()) // 10))  # 1 point per 10 words, max 10
                    relevance_score = min(10, max(1, len(set(user_answer.lower().split()) & set(st.session_state.current_question["question"].lower().split())) // 5))  # 1 point per 5 matching words, max 10
                    completeness_score = min(10, max(1, len(user_answer) // 20))  # 1 point per 20 characters, max 10
                    
                    # Overall score calculation
                    overall_score = (similarity * 0.4 + clarity_score * 0.2 + relevance_score * 0.2 + completeness_score * 0.2)
                    
                    # Generate detailed feedback
                    feedback_parts = []
                    
                    # Overall assessment
                    if overall_score >= 8:
                        feedback_parts.append("🌟 **Excellent!** Outstanding answer that demonstrates strong understanding.")
                    elif overall_score >= 6:
                        feedback_parts.append("👍 **Good!** Solid answer with room for minor improvements.")
                    elif overall_score >= 4:
                        feedback_parts.append("📝 **Fair!** Adequate answer that addresses the basics.")
                    else:
                        feedback_parts.append("⚠️ **Needs Work!** Answer requires significant improvement.")
                    
                    # Specific feedback
                    if clarity_score < 5:
                        feedback_parts.append(f"\n\n**📝 Clarity ({clarity_score}/10):** Structure your answer better with clear introduction, body, and conclusion.")
                    else:
                        feedback_parts.append(f"\n\n**📝 Clarity ({clarity_score}/10):** Well-structured and easy to understand.")
                    
                    if relevance_score < 5:
                        feedback_parts.append(f"\n\n**🎯 Relevance ({relevance_score}/10):** Ensure your answer directly addresses the question asked.")
                    else:
                        feedback_parts.append(f"\n\n**🎯 Relevance ({relevance_score}/10):** Good alignment with the question requirements.")
                    
                    if completeness_score < 5:
                        feedback_parts.append(f"\n\n**📊 Completeness ({completeness_score}/10):** Add more details and examples to make your answer comprehensive.")
                    else:
                        feedback_parts.append(f"\n\n**📊 Completeness ({completeness_score}/10):** Good coverage of the key concepts.")
                    
                    # Sample answer comparison
                    feedback_parts.append(f"\n\n**💡 Sample Answer Analysis:**")
                    if similarity >= 70:
                        feedback_parts.append("Your answer closely matches the expected response.")
                    elif similarity >= 50:
                        feedback_parts.append("Your answer covers many key points from the sample.")
                    else:
                        feedback_parts.append("Review the sample answer for key concepts you may have missed.")
                    
                    # Improvement suggestions
                    feedback_parts.append(f"\n\n**🚀 Improvement Suggestions:**")
                    if clarity_score < 7:
                        feedback_parts.append("- Structure your answer with clear introduction, body, and conclusion.")
                    if relevance_score < 7:
                        feedback_parts.append("- Include more keywords and concepts from the question.")
                    if completeness_score < 7:
                        feedback_parts.append("- Provide specific examples and elaborate on your points.")
                    
                    detailed_feedback = "".join(feedback_parts)
                    
                    st.session_state.feedback = {
                        'score': round(overall_score * 10),
                        'clarity': clarity_score,
                        'relevance': relevance_score,
                        'completeness': completeness_score,
                        'detailed_feedback': detailed_feedback,
                        'similarity_score': similarity
                    }
                else:
                    st.warning("Please provide an answer before submitting.")
        
        # Show feedback
        if st.session_state.get("show_feedback", False):
            st.subheader("📝 Feedback & Analysis")
            feedback = st.session_state.feedback
            
            # Score metrics
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Overall Score", f"{feedback.get('score', 0)}/100")
                st.metric("Word Count", len(st.session_state.user_answer.split()))
            with col2:
                st.metric("Similarity", f"{feedback.get('similarity_score', 0):.1f}%")
            
            # Detailed breakdown
            st.write("### 📊 Score Breakdown:")
            st.write(f"- **Clarity ({feedback.get('clarity', 0)}/10):** {'Well-structured' if feedback.get('clarity') >= 7 else 'Needs improvement'}")
            st.write(f"- **Relevance ({feedback.get('relevance', 0)}/10):** {'On target' if feedback.get('relevance') >= 7 else 'Off topic'}")
            st.write(f"- **Completeness ({feedback.get('completeness', 0)}/10):** {'Comprehensive' if feedback.get('completeness') >= 7 else 'Needs more detail'}")
            
            # Feedback text
            st.write("### 📝 Detailed Feedback:")
            st.write(feedback.get('detailed_feedback', "No feedback available."))
            
            # Sample answer for comparison
            with st.expander("💡 Sample Answer for Reference"):
                st.info(st.session_state.current_question.get("sample_answer", "No sample answer available."))
            
            # Action buttons
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 Try Again"):
                    st.session_state.show_feedback = False
                    st.session_state.user_answer = ""
                    st.rerun()
            
            with col2:
                if st.button("📚 View Sample Answer"):
                    st.session_state.show_sample_answer = not st.session_state.get("show_sample_answer", False)
                    st.rerun()
    
    elif page == "Question Bank":
        st.header("📚 Question Bank")
        
        # Filters
        col1, col2 = st.columns(2)
        with col1:
            filter_difficulty = st.selectbox("Filter by difficulty", ["All"] + list(set([q.get('difficulty') for q in questions])))
        with col2:
            filter_topic = st.selectbox("Filter by topic", ["All"] + list(set([q.get('topic') for q in questions])))
        
        # Search
        search_query = st.text_input("Search questions...")
        
        # Get filtered questions
        filtered_questions = questions.copy()
        if filter_difficulty != "All":
            filtered_questions = [q for q in filtered_questions if q.get('difficulty') == filter_difficulty]
        if filter_topic != "All":
            filtered_questions = [q for q in filtered_questions if q.get('topic') == filter_topic]
        
        # Display results
        if st.button("Search Questions") or search_query:
            if filtered_questions:
                st.write(f"Found {len(filtered_questions)} questions:")
                for i, q in enumerate(filtered_questions[:10], 1):
                    with st.expander(f"Q{i}: {q['question'][:50]}..."):
                        st.write("**Question:**")
                        st.write(q["question"])
                        st.write("**Topic:**", q["topic"])
                        st.write("**Difficulty:**", q["difficulty"])
                        with st.expander("💡 Sample Answer"):
                            st.info(q.get("sample_answer", "No sample answer available."))
            else:
                st.info("No questions found matching your criteria.")
    
    elif page == "Progress":
        st.header("📊 Progress Tracking")
        
        # Simple progress tracking
        if "practice_sessions" not in st.session_state:
            st.session_state.practice_sessions = []
        
        if st.button("Record Practice Session"):
            if "current_question" in st.session_state and "user_answer" in st.session_state:
                session = {
                    "question": st.session_state.current_question,
                    "user_answer": st.session_state.user_answer,
                    "score": st.session_state.feedback.get("score", 0),
                    "timestamp": str(st.session_state.get("timestamp", "")),
                    "clarity": st.session_state.feedback.get("clarity", 0),
                    "relevance": st.session_state.feedback.get("relevance", 0),
                    "completeness": st.session_state.feedback.get("completeness", 0)
                }
                st.session_state.practice_sessions.append(session)
                st.success(f"Session recorded! Total sessions: {len(st.session_state.practice_sessions)}")
        
        if st.session_state.practice_sessions:
            st.subheader("📈 Your Progress")
            
            # Calculate average scores
            scores = [s.get("score", 0) for s in st.session_state.practice_sessions]
            clarity_scores = [s.get("clarity", 0) for s in st.session_state.practice_sessions]
            relevance_scores = [s.get("relevance", 0) for s in st.session_state.practice_sessions]
            completeness_scores = [s.get("completeness", 0) for s in st.session_state.practice_sessions]
            
            if scores:
                avg_score = sum(scores) / len(scores)
                avg_clarity = sum(clarity_scores) / len(clarity_scores)
                avg_relevance = sum(relevance_scores) / len(relevance_scores)
                avg_completeness = sum(completeness_scores) / len(completeness_scores)
                
                # Metrics
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Average Score", f"{avg_score:.1f}/100")
                    st.metric("Total Sessions", len(st.session_state.practice_sessions))
                with col2:
                    st.metric("Avg Clarity", f"{avg_clarity:.1f}/10")
                    st.metric("Avg Relevance", f"{avg_relevance:.1f}/10")
                
                # Progress chart
                st.subheader("📈 Score Progress")
                st.line_chart([s.get("score", 0) for s in st.session_state.practice_sessions])
                
                # Session details
                st.subheader("📝 Session History")
                for i, session in enumerate(reversed(st.session_state.practice_sessions[-5:]), 1):
                    with st.expander(f"Session {len(st.session_state.practice_sessions) - i + 1}"):
                        st.write(f"**Question:** {session['question'][:100]}...")
                        st.write(f"**Score:** {session['score']}/100")
                        st.write(f"**Date:** {session['timestamp']}")
            else:
                st.info("No practice sessions recorded yet.")
    
    # Footer
    st.markdown("---")
    st.markdown("💡 **Tip:** Practice regularly and focus on areas where you need improvement!")
    st.markdown(f"📊 **Total Questions Available:** {len(questions)}")

else:
    st.error("❌ No interview questions found. Please check if dataset/interview_qa.json exists.")
    st.markdown("""
    ### Expected dataset structure:
    ```json
    [
        {
            "question": "Your question here",
            "difficulty": "Easy|Medium|Hard",
            "topic": "Technical|Behavioral|System Design|Problem Solving|General",
            "sample_answer": "Sample answer for comparison"
        }
    ]
    ```
