from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .schemas import QueryRequest, QueryResponse
from .agent import math_agent, AgentState
from .guardrails import is_math_question, moderate_output
# In a real app, feedback would be persisted, here we store the last one
from .feedback import refine_answer_with_feedback

app = FastAPI()

# --- CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allows React app to connect
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store last conversation for feedback
last_conversation = {}

@app.post("/query", response_model=QueryResponse)
async def handle_query(request: QueryRequest):
    global last_conversation

    # 1. Input Guardrail
    if not is_math_question(request):
        raise HTTPException(
            status_code=400,
            detail="This agent only answers math-related questions."
        )

    # 2. Run the agentic graph
    initial_state = AgentState(original_question=request.question)
    final_state = math_agent.invoke(initial_state)

    if final_state.get("error"):
        raise HTTPException(status_code=500, detail=final_state["error"])

    # 3. Output Guardrail
    final_answer = moderate_output(final_state["answer"])
    
    # Store for potential feedback
    last_conversation = {
        "question": request.question,
        "answer": final_answer,
        "source": final_state["source"]
    }

    return QueryResponse(
        answer=final_answer,
        source=final_state["source"]
    )

@app.post("/feedback")
async def handle_feedback(feedback_data: dict):
    global last_conversation
    feedback_text = feedback_data.get("feedback")
    
    if not feedback_text or not last_conversation:
        raise HTTPException(status_code=400, detail="No active conversation to give feedback on.")

    # Use DSPy to refine the answer
    refined = refine_answer_with_feedback(
        question=last_conversation["question"],
        answer=last_conversation["answer"],
        feedback=feedback_text
    )
    
    # Update the last answer with the refined one
    last_conversation["answer"] = refined
    
    return {"message": "Feedback received and answer updated.", "refined_answer": refined}