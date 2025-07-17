from utils.config import GROQ_API_KEY,LLM_MODEL,TEMPERATURE
from langchain_groq import ChatGroq
from langgraph.types import Command,interrupt
import os 
from models.state import MediState,ralph_system_prompt
from typing_extensions import Literal
from langgraph.graph import StateGraph,START,END
from langchain_core.messages import HumanMessage,AIMessage,SystemMessage,ToolMessage
from tools.tools import (check_availability_by_doctor,
                          check_availability_by_specialization,
                          set_appointment,
                          cancel_appointment,
                          reschedule_appointment)
from dotenv import load_dotenv
load_dotenv()

tools = [check_availability_by_doctor,check_availability_by_specialization,set_appointment,cancel_appointment,reschedule_appointment]

class AgentNodes:
    def __init__(self):
        self.llm = ChatGroq(model=LLM_MODEL,temperature=TEMPERATURE,api_key=GROQ_API_KEY).bind_tools(tools=tools)
        
    def assistant_node(self,state:MediState):
        response = self.llm.invoke(
            [SystemMessage(content=ralph_system_prompt)]+
            state.messages
        )
        state.messages += [response]
        return state

    def human_tool_review_node(self,state:MediState) -> Command[Literal["assistant_node", "tools"]]:
        last_message = state.messages[-1]
        
        if not isinstance(last_message, AIMessage) or not last_message.tool_calls:
            # Changed from raise ValueError to a softer Command
            # This makes the graph more resilient to unexpected states
            print("Warning: human_tool_review_node received a message without valid tool calls or not an AIMessage. Returning to assistant.")
            return Command(goto="assistant_node", update={"messages": [HumanMessage(content="It seems I tried to call a tool, but something went wrong or it wasn't a valid tool call. Can you please rephrase or clarify your request?")]})

        tool_call = last_message.tool_calls[-1]
        human_review: dict = interrupt({
            "message": "Your input is required for the following tool:",
            "tool_call": tool_call
        })
        review_action = human_review.get("action")
        # review_data = human_review.get("data") # This line was present but review_data isn't used after

        if review_action == "continue":
            return Command(goto="tools")
        
        elif review_action == "reject":
            tool_message = ToolMessage(
                content="The tool call was rejected by the user, follow up with the user to understand why and how they would like to proceed.",
                name=tool_call["name"],
                tool_call_id=tool_call["id"]
            )
            return Command(goto="assistant_node", update={"messages": [tool_message]})
        
        else: # Default if action is not 'continue' or 'reject' (e.g., user just hits enter)
            return Command(goto="tools")
        
    def assistant_router(self,state:MediState):
        last_message = state.messages[-1]
        # Robust check for AIMessage and tool_calls
        if isinstance(last_message, AIMessage) and last_message.tool_calls:
            if not state.yolo_mode:
                if any(tool_call["name"] in state.protected_tools for tool_call in last_message.tool_calls):
                    return "human_tool_review_node"
            return "tools"
        else:
            return END