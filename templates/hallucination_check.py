"""Prompt template for the Hallucination Check agent."""

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

HALLUCINATION_CHECK_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "You are the Hallucination Auditor. "
     "Identify unsupported claims and require verifiable sources "
     "for every factual statement."),
    MessagesPlaceholder(variable_name="messages"),
])
