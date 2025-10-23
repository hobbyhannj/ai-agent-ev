"""Prompt template for the Cross-Layer Validation agent."""

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

CROSS_LAYER_VALIDATION_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "You are the Cross-Layer Validator. "
     "Ensure consistency and alignment among market, policy, OEM, "
     "supply chain, and finance insights."),
    MessagesPlaceholder(variable_name="messages"),
])
