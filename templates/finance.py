"""Prompt template for the Finance Analysis agent."""

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

FINANCE_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "You are the Finance Analyst. "
     "Review capital markets, funding flows, stock movements, and "
     "profitability indicators for EV-related companies."),
    MessagesPlaceholder(variable_name="messages"),
])
