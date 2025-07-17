# 🤖 LangGraph-Based Intelligent Appointment System

A multi-agent AI system for managing doctor appointments using **LangGraph**, **LangChain**, and **Groq LLMs** — with **selective Human-in-the-Loop (HITL)** governance for sensitive operations and **LangSmith** for tracking and debugging.

---

## 🔍 Overview

This system automates the management of doctor appointments, offering a robust and scalable solution with the following capabilities:
- ✔️ **Appointment Availability Checks**: Query doctor schedules efficiently.
- 🗓️ **Booking Appointments**: Secure slots with human oversight.
- 🔁 **Rescheduling**: Modify existing appointments with approval.
- ❌ **Cancellation**: Cancel appointments securely.

🧠 **Human-in-the-Loop (HITL) Design**:  
Critical actions (`book_appointment`, `cancel_appointment`, `reschedule_appointment`) require explicit human approval to ensure trust and accuracy, while non-sensitive tasks (e.g., `check_availability`) run autonomously.

🛠️ **LangSmith Integration**:  
The system leverages **LangSmith** for tracing and debugging agent workflows, providing visibility into LangGraph's execution for performance monitoring and optimization.

---

## 🧩 Key Features

| Agent                     | Description                                  | HITL Required |
|--------------------------|----------------------------------------------|----------------|
| `check_availability`     | Queries doctor's schedule from CSV           | ❌ No          |
| `book_appointment`       | Books a new appointment                      | ✅ Yes         |
| `cancel_appointment`     | Cancels an existing appointment              | ✅ Yes         |
| `reschedule_appointment` | Changes appointment date/time                | ✅ Yes         |
| `inform_user`            | Sends user notifications and responses       | ❌ No          |

### LangSmith Highlights
- **Traceability**: Tracks agent execution paths, inputs, and outputs in LangGraph workflows.
- **Debugging**: Identifies bottlenecks or errors in multi-agent interactions.
- **Monitoring**: Provides insights into HITL decision points and agent performance.

---

## 🚀 Tech Stack

- **LangGraph**: Orchestrates multi-agent workflows with stateful graph-based execution.
- **LangChain**: Manages LLM orchestration, tool integration, and prompt engineering.
- **Groq LLM**: Powers fast and efficient language model inference.
- **Pandas**: Handles CSV-based data storage for schedules and appointments.
- **Streamlit / FastAPI**: Optional interfaces for user interaction (frontend/backend).
- **LangSmith**: Enables tracing, debugging, and performance monitoring of workflows.

---

## 🔁 Human-in-the-Loop Flow

1. **User Input**: User submits a request (e.g., "Book an appointment for next Tuesday").
2. **LLM Parser**: Identifies intent using LangChain's parsing capabilities.
3. **Decision Point**:
   - If intent involves `book`, `cancel`, or `reschedule`:
     - 🔒 Pauses workflow and prompts for human approval.
     - 🧑‍⚖️ Human reviews request details and confirms/rejects.
   - Else: Non-sensitive tasks (e.g., availability checks) proceed autonomously.
4. **Execution**: Approved actions are executed, and results are logged in LangSmith.
5. **Response**: User receives confirmation via the `inform_user` agent.

---

## 📂 Folder Structure

```
├── /agents/                    # Agent-specific logic
│   ├─ Agents                   
├── /workflow/                  # LangGraph workflow definitions
│   ├── graph.py                # Core graph execution logic
├── /data/                      # Data storage
│   ├── availability.csv        # Doctor schedules
├── /tools/                    
│   └── tools.py                # All tools functions (set appointment,cancel appointment..) 
├── chat_local.py                # Entry point for the application run application in terminal 
├── requirements.txt            # Project dependencies
└── README.md                   # This file
```

---

## 🛠️ Setup Instructions

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/ldotmithu/LangGraph-Intelligent-Appointment-System.git
   cd LangGraph-Intelligent-Appointment-System
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set Up Environment Variables**:
   Create a `.env` file with the following:
   ```env
   GROQ_API_KEY=your_groq_api_key
   LANGSMITH_API_KEY=your_langsmith_api_key
   ```

4. **Run the Application**:
   ```bash
   python chat_local.py
   ```
---

## 📊 LangSmith Integration

To enable LangSmith tracing:
1. Ensure your `LANGSMITH_API_KEY` is set in the `.env` file.
2. Configure LangGraph to log traces:
   ```python
   from langsmith import Client
   client = Client()
   ```
3. Monitor workflows in the LangSmith dashboard for detailed insights into agent execution, HITL interactions, and performance metrics.

---

## 📣 Credits

- **Author**: ❤️ Mithurshan 
- **Technologies**: Built with LangChain, LangGraph, Groq, and LangSmith.
- **Inspiration**: Designed for real-world applications requiring high trust and transparency in AI systems.

---

## 📬 Contact

For collaboration or questions, reach out via [LinkedIn](https://www.linkedin.com/in/mithurshan6).