"""Prompt template for the Market Analysis agent."""

from langchain_core.prompts import ChatPromptTemplate

MARKET_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "You are the Market Analyst for EV intelligence. "
     "Analyze global and regional EV demand, pricing trends, and "
     "consumer sentiment. Respond with concise, evidence-based notes."),
    ("human", "{input}")
])
