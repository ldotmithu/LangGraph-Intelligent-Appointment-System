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

    def human_tool_review_node(self,state:MediState)-> Command[Literal["assistant_node", "tools"]]:
        last_message = state.messages[-1]
        tool_call = last_message.tool_calls[-1]
        
        human_review :dict = interrupt({
            "message":"Your input is required for the following tool:",
            "tool_call":tool_call
        })
        
        review_action = human_review.get("action")
        
        if review_action=="continue":
            return Command(goto="tools")
        
        elif review_action =="reject":
            tool_message = ToolMessage(
                content="The tool call was rejected by the user, follow up with the user to understand why and how they would like to proceed",
                name = tool_call["name"],
                tool_call_id = tool_call["id"]
            )
            return Command(goto="assistant_node",update={"messages":[tool_message]})
        
        else:
            # if press entire 
            return Command(goto="tools")
        
    def assistant_router(self,state:MediState):
        last_message = state.messages[-1]    
        if not last_message.tool_calls:
            return END
        else:
            if not state.yolo_mode:
                if any(tool_call["name"] in state.protected_tools for tool_call in last_message.tool_calls):
                    return "human_tool_review_node"
            return "tools"   
    

            
        
        
        
        
        
    
