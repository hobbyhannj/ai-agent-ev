"""Prompt template for the Policy Analysis agent."""

from langchain_core.prompts import ChatPromptTemplate

POLICY_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "You are the Policy Analyst. "
     "Evaluate government policies, incentives, and trade regulations "
     "affecting the EV industry. Focus on actionable insights."),
    ("human", "{input}")
])
