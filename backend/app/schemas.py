from pydantic import BaseModel
from typing import List, Optional

# API Schemas
class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str
    source: str
    feedback_needed: bool = True

# Agent State (MCP - Model Context Protocol)
class AgentState(BaseModel):
    original_question: str
    answer: Optional[str] = None
    source: str = "N/A"
    context: Optional[str] = None
    feedback: Optional[str] = None
    error: Optional[str] = None