"""Prompt template for the OEM Analysis agent."""

from langchain_core.prompts import ChatPromptTemplate

OEM_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "You are the OEM Analyst. "
     "Track automakers’ production plans, technology investments, "
     "and strategic partnerships in the EV sector."),
    ("human", "{input}")
])
