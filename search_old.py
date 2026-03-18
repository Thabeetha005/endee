import random
import json
from typing import List, Dict, Any, Optional
from embedder import EmbeddingManager
import re

class InterviewSearch:

    if filters:
        results = index.query(
            vector=qvec,
            top_k=top_k,
            filter=filters
        )
    else:
        results = index.query(
            vector=qvec,
            top_k=top_k
        )

    return results