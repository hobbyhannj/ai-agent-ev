"""Prompt template for the OEM Analysis agent."""

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

OEM_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "You are the OEM Analyst. "
     "Track automakers’ production plans, technology investments, "
     "and strategic partnerships in the EV sector."),
    MessagesPlaceholder(variable_name="messages"),
])
