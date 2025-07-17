# backend/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncio
from typing import List, Optional, Union, Dict, Any
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
from langgraph.checkpoint.memory import MemorySaver 
from workflow.graph import build_graph
from langgraph.types import Interrupt # Import Interrupt

app = FastAPI()
graph = None 

@app.on_event("startup")
async def startup_event():
    global graph
    print("Initializing LangGraph...")
    graph = build_graph()
    print("LangGraph initialized.")

class ChatRequest(BaseModel):
    user_input: Optional[str] = None # user_input can be None if it's a human_response
    thread_id: str 
    human_response: Optional[Dict[str, str]] = None # {"action": "continue"/"reject", "data": "reason"}

class ChatResponse(BaseModel):
    response: str
    full_messages: List[Dict[str, Any]]
    requires_human_input: bool = False
    human_input_prompt: Optional[Dict[str, Any]] = None # e.g., {"message": "...", "tool_call": {}}

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    if graph is None:
        raise HTTPException(status_code=503, detail="LangGraph not initialized yet.")

    config = {"configurable": {"thread_id": request.thread_id}}
    
    # Determine the initial state or input to the graph
    graph_input = {}
    if request.human_response:
        # If human_response is present, it means we are resuming an interrupted graph
        # and feeding the human's decision back to the interrupt point.
        graph_input = request.human_response 
    elif request.user_input is not None:
        # Otherwise, if user_input is present, it's a new user query
        initial_state = {
            "messages": [HumanMessage(content=request.user_input)],
            "yolo_mode": False 
        }
        graph_input = initial_state
    else:
        raise HTTPException(status_code=400, detail="Either 'user_input' or 'human_response' must be provided.")

    try:
        output = graph.invoke(
            graph_input,
            config=config # Pass the thread_id config
        )
        
        # --- Handle Interruptions ---
        # The result of `invoke` will be an `Interrupt` object if the graph interrupted
        if isinstance(output, Interrupt):
            print(f"Graph interrupted! Data: {output.data}")
            return ChatResponse(
                response="Awaiting human confirmation for tool execution.",
                full_messages=[], # We don't have a new message from the assistant yet
                requires_human_input=True,
                human_input_prompt=output.data # This will be the dict from interrupt(...)
            )

        # --- Handle Normal Graph Completion ---
        response_message = ""
        serializable_messages = []

        if output and output.get("messages"):
            # Prepare messages for serialization
            for msg in output["messages"]:
                if isinstance(msg, (HumanMessage, AIMessage, SystemMessage, ToolMessage)):
                    serializable_messages.append({
                        "type": msg.type, 
                        "content": msg.content, 
                        "tool_calls": [tc.dict() for tc in msg.tool_calls] if getattr(msg, 'tool_calls', None) else None,
                        "name": msg.name if hasattr(msg, 'name') else None,
                        "tool_call_id": msg.tool_call_id if hasattr(msg, 'tool_call_id') else None
                    })
                else:
                    serializable_messages.append({"type": "unknown", "content": str(msg)})

            # Find the last relevant message for the main response display
            for msg in reversed(output["messages"]):
                if isinstance(msg, AIMessage) and msg.content:
                    response_message = msg.content
                    break
                elif msg.content: 
                    response_message = msg.content
                    break
            
            if not response_message:
                # If no content found, try to represent tool calls or message type
                last_msg_raw = output["messages"][-1]
                if getattr(last_msg_raw, 'tool_calls', None):
                    response_message = f"Agent suggested tool call(s): {[tc.name for tc in last_msg_raw.tool_calls]}"
                elif last_msg_raw.type:
                    response_message = f"Agent responded with a message of type: {last_msg_raw.type} (no content)."

        return ChatResponse(response=response_message, full_messages=serializable_messages)

    except Exception as e:
        print(f"Error during graph invocation: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")