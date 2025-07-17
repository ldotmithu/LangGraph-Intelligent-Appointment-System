from workflow.graph import build_graph
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langchain_core.messages import BaseMessage
from langchain.callbacks.tracers import LangChainTracer
import os
from utils.config import LANGSMITH_API_KEY,LANGSMITH_PROJECT
from dotenv import load_dotenv
load_dotenv()

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

def get_message_emoji(msg: BaseMessage):
    if isinstance(msg, HumanMessage):
        return "🧑‍💬 (You)"
    elif isinstance(msg, AIMessage):
        return "🤖 (Assistant)"
    elif isinstance(msg, ToolMessage):
        return "🛠️ (Tool Result)"
    else:
        return "📦 (Other)"

def main():
    print(f"{Colors.BOLD}🤖 Welcome to the Multi-Agent Assistant! Type 'exit' to quit.{Colors.END}\n")
    graph = build_graph()
    os.environ["LANGSMITH_API_KEY"] = LANGSMITH_API_KEY
    
    os.environ["LANGSMITH_PROJECT"] = LANGSMITH_PROJECT
    

    while True:
        user_input = input(f"{Colors.OKBLUE}🧑 You: {Colors.END}")
        if user_input.strip().lower() == "exit":
            print(f"{Colors.OKGREEN}👋 Exiting... Have a great day!{Colors.END}")
            break

        initial_state = {
            "messages": [HumanMessage(content=user_input)]
        }

        tracer = LangChainTracer()
        try:
            output = graph.invoke(
        initial_state,
        config={
            "configurable": {"thread_id": "new-test-thread-id"},
            "callbacks": [tracer],
            "run_name": "Appointment Assistant with Review"
        }
    )
            print(f"\n{Colors.BOLD}📡 Assistant Conversation Output:{Colors.END}")

            for msg in output["messages"]:
                emoji = get_message_emoji(msg)

                # Highlight tool usage from AI message
                if isinstance(msg, AIMessage):
                    print(f"{emoji} {Colors.OKCYAN}{msg.content}{Colors.END}")
                    if hasattr(msg, "tool_calls") and msg.tool_calls:
                        for tool_call in msg.tool_calls:
                            tool_name = tool_call["name"]
                            tool_args = tool_call["args"]
                            print(f"   🛠️ Tool Called: {Colors.OKGREEN}{tool_name}{Colors.END}")
                            print(f"   📤 Args Sent : {tool_args}")
                elif isinstance(msg, ToolMessage):
                    print(f"{emoji} {Colors.OKGREEN}Tool Output: {msg.content}{Colors.END}")
                elif isinstance(msg, HumanMessage):
                    print(f"{emoji} {Colors.OKBLUE}{msg.content}{Colors.END}")
                else:
                    print(f"{emoji} {msg.content}")

            print(f"{Colors.OKBLUE}" + "─" * 60 + f"{Colors.END}\n")

        except Exception as e:
            print(f"{Colors.FAIL}❌ Error: {e}{Colors.END}\n")

if __name__ == "__main__":
    main()
