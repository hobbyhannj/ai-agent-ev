"""Prompt template for the Supply Chain Analysis agent."""

from langchain_core.prompts import ChatPromptTemplate

SUPPLY_CHAIN_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "You are the Supply Chain Analyst. "
     "Examine suppliers, material availability, logistics issues, "
     "and potential bottlenecks in EV manufacturing."),
    ("human", "{input}")
])
