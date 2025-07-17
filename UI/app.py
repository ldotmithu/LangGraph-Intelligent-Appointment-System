import os
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, END, START
from langgraph.prebuilt import ToolNode
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from agents.Agents import AgentNodes
from models.state import MediState
from tools.tools import (
    check_availability_by_doctor,
    check_availability_by_specialization,
    set_appointment,
    cancel_appointment,
    reschedule_appointment
)

# Initialize your graph
nodes = AgentNodes()
tools = [check_availability_by_doctor, check_availability_by_specialization, set_appointment, cancel_appointment, reschedule_appointment]

builder = StateGraph(MediState)
builder.add_node("assistant_node", nodes.assistant_node)
builder.add_node("human_tool_review_node", nodes.human_tool_review_node)
builder.add_node("tools", ToolNode(tools))

builder.add_edge(START, "assistant_node")
builder.add_conditional_edges("assistant_node", nodes.assistant_router, ["tools", "human_tool_review_node", END])
builder.add_edge("tools", "assistant_node")
builder.add_edge("human_tool_review_node", "assistant_node") # This is crucial for returning to the assistant after review

graph = builder.compile(checkpointer=MemorySaver())

# --- CLI Interaction ---
def run_cli_agent():
    print("Welcome to Ralph, your medical appointment assistant!")
    print("Type 'exit' to quit.")

    thread_id = "my_user_session" # You can use a unique ID per user if needed
    config = {"configurable": {"thread_id": thread_id}}

    while True:
        user_input = input("\nYou: ")
        if user_input.lower() == 'exit':
            print("Goodbye!")
            break

        # Check if the graph is currently interrupted (waiting for human review)
        current_state = graph.get_state(config)
        if current_state.next and "human_tool_review_node" in current_state.next:
            # If interrupted, the user input is the human's decision
            try:
                # The interrupt expects a dictionary with "action" and "data"
                # For 'continue' or 'reject', 'data' might be empty or a message
                action = user_input.lower()
                if action in ["yes", "y", "approve", "continue"]:
                    human_response_data = {"action": "continue"}
                elif action in ["no", "n", "reject"]:
                    human_response_data = {"action": "reject"}
                else:
                    print("Invalid input for tool review. Please type 'yes' or 'no'.")
                    continue
                
                # Invoke the graph with the human's response to the interrupt
                for s in graph.stream(human_response_data, config=config):
                    # Process and print output as it streams
                    if "__end__" not in s:
                        for key, value in s.items():
                            if key == "assistant_node":
                                last_message = value["messages"][-1]
                                if isinstance(last_message, AIMessage):
                                    if last_message.tool_calls:
                                        # The assistant is suggesting a tool call, the human_tool_review_node will handle the interruption
                                        print(f"Ralph (Tool Suggestion): {last_message.tool_calls}")
                                        print("--- HUMAN REVIEW REQUIRED ---")
                                        print("Do you approve this tool call? (yes/no)")
                                    else:
                                        print(f"Ralph: {last_message.content}")
                                elif isinstance(last_message, ToolMessage):
                                    print(f"Tool Executed: {last_message.content}")

            except Exception as e:
                print(f"Error during human review: {e}")
                print("Please try again.")
        else:
            # If not interrupted, it's a regular user message
            print("Ralph is thinking...")
            for s in graph.stream({"messages": [HumanMessage(content=user_input)]}, config=config):
                # Process and print output as it streams
                if "__end__" not in s:
                    for key, value in s.items():
                        if key == "assistant_node":
                            last_message = value["messages"][-1]
                            if isinstance(last_message, AIMessage):
                                if last_message.tool_calls:
                                    print(f"Ralph (Tool Suggestion): {last_message.tool_calls}")
                                    print("--- HUMAN REVIEW REQUIRED ---")
                                    print("Do you approve this tool call? (yes/no)")
                                else:
                                    print(f"Ralph: {last_message.content}")
                            elif isinstance(last_message, ToolMessage):
                                print(f"Tool Executed: {last_message.content}")
                        # You can add other nodes here if you want to see their output

if __name__ == "__main__":
    run_cli_agent()