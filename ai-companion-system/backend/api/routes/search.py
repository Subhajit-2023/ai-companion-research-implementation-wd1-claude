"""
Web Search API Routes
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))
from api.services.search_service import search_service
from config import settings


router = APIRouter()


class SearchRequest(BaseModel):
    query: str
    max_results: Optional[int] = None


@router.post("/")
async def search_web(request: SearchRequest):
    """Search the web"""
    if not settings.ENABLE_WEB_SEARCH:
        raise HTTPException(status_code=503, detail="Web search is disabled")

    results = await search_service.search(
        request.query,
        max_results=request.max_results
    )

    summary = await search_service.summarize_results(results)

    return {
        "query": request.query,
        "results": results,
        "summary": summary,
        "count": len(results)
    }


@router.post("/news")
async def search_news(request: SearchRequest):
    """Search for news"""
    if not settings.ENABLE_WEB_SEARCH:
        raise HTTPException(status_code=503, detail="Web search is disabled")

    results = await search_service.search_news(
        request.query,
        max_results=request.max_results
    )

    return {
        "query": request.query,
        "results": results,
        "count": len(results)
    }


@router.get("/quick-answer")
async def get_quick_answer(query: str):
    """Get quick answer to a query"""
    if not settings.ENABLE_WEB_SEARCH:
        raise HTTPException(status_code=503, detail="Web search is disabled")

    answer = await search_service.quick_answer(query)

    if not answer:
        return {
            "query": query,
            "answer": None,
            "message": "No quick answer available"
        }

    return {
        "query": query,
        "answer": answer
    }


@router.get("/current-info")
async def get_current_info(topic: str):
    """Get current information about a topic"""
    if not settings.ENABLE_WEB_SEARCH:
        raise HTTPException(status_code=503, detail="Web search is disabled")

    info = await search_service.get_current_info(topic)

    return {
        "topic": topic,
        "information": info
    }
