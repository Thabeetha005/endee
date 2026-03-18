# AI Interview Preparation Bot using Endee

## Project Overview
This project is an AI-powered Interview Preparation Bot built using Endee as the vector database. It helps users search and retrieve relevant interview questions and answers semantically instead of relying only on keyword search.

## Use Case
Students and job seekers can prepare for interviews in topics like Java, Python, DBMS, OS, and Aptitude by asking natural language queries such as:
- "Java OOP interview questions"
- "DBMS normalization questions"
- "Operating system deadlock explanation"

## System Design
User Query -> Embedding Model -> Endee Vector Search -> Top-K Relevant Interview Q&A -> Streamlit UI

## How Endee is Used
- Endee stores embeddings of interview questions and answers
- Endee performs semantic similarity search
- Endee uses filters for topic and difficulty
- Endee returns top-k matching interview records

## Tech Stack
- Python
- Streamlit
- Sentence Transformers
- Endee Vector Database

## Setup Instructions

### 1. Start Endee
Run Endee locally using Docker on port 8080.

### 2. Install dependencies
pip install -r requirements.txt

### 3. Ingest dataset
python ingest.py

### 4. Run application
streamlit run app.py

## Features
- Semantic search
- Topic filter
- Difficulty filter
- Interview answer retrieval
- Simple UI

## Future Improvements
- Add LLM-generated explanations
- Add mock interview mode
- Add quiz mode
- Add interview recommendations