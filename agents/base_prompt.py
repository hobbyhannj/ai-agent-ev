from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

def build_prompt(system_instruction: str) -> ChatPromptTemplate:
    """LangGraph-safe base prompt (for agents & supervisor)."""
    return ChatPromptTemplate.from_messages([
        ("system", system_instruction),
        MessagesPlaceholder(variable_name="messages"),
    ])
