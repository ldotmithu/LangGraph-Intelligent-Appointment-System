from pydantic import BaseModel
from typing_extensions import List,Optional,TypedDict,Annotated
from langgraph.graph.message import add_messages
from langchain_core.messages.base import BaseMessage

ralph_system_prompt = "You are a medical appointment assistant. Help patients schedule, cancel, or reschedule appointments. Always ask for all required information before calling a tool."

protected_tools = ["set_appointment", "cancel_appointment", "reschedule_appointment"]

class MediState(BaseModel):
    messages: Annotated[List[BaseMessage], add_messages] = []
    protected_tools: List[str] = protected_tools
    yolo_mode: bool = False