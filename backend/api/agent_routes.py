"""
Routes HTTP pour l'agent IA (Phase 2).
"""
from fastapi import APIRouter
from pydantic import BaseModel

from backend.agents.orchestrator import run_agent

router = APIRouter()


class AgentAskRequest(BaseModel):
    question: str


class AgentAskResponse(BaseModel):
    answer: str
    tool_calls: list[str]


@router.post("/ask", response_model=AgentAskResponse)
async def agent_ask(payload: AgentAskRequest):
    """Pose une question à l'agent, qui choisit et appelle les outils nécessaires."""
    result = run_agent(payload.question)
    return AgentAskResponse(answer=result.answer, tool_calls=result.tool_calls)