"""Prompt template for the Report Quality Check agent."""

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

REPORT_QUALITY_CHECK_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "You are the Report Quality Reviewer. "
     "Assess overall structure, clarity, completeness, and factual accuracy "
     "of the generated EV market report."),
    MessagesPlaceholder(variable_name="messages"),
])
