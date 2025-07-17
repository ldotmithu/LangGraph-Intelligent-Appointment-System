from agents.Agents import AgentNodes
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph,END,START
from models.state import MediState
from langgraph.prebuilt import ToolNode
from tools.tools import (check_availability_by_doctor,
                          check_availability_by_specialization,
                          set_appointment,
                          cancel_appointment,
                          reschedule_appointment)

tools = [check_availability_by_doctor,check_availability_by_specialization,set_appointment,cancel_appointment,reschedule_appointment]

def build_graph(nodes = AgentNodes()): 
    builder = StateGraph(MediState)
    builder.add_node("assistant_node", nodes.assistant_node) 
    builder.add_node("human_tool_review_node", nodes.human_tool_review_node) 
    builder.add_node("tools",ToolNode(tools)) 
    
    builder.add_edge(START,"assistant_node")
    builder.add_conditional_edges(
        "assistant_node",
        nodes.assistant_router,
        {
            "tools": "tools",
            "human_tool_review_node": "human_tool_review_node",
            END: END 
        }
    )
    builder.add_edge("tools", "assistant_node")
    builder.add_edge("human_tool_review_node", "assistant_node") 
    
    return builder.compile(checkpointer=MemorySaver())