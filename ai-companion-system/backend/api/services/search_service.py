"""
Web Search Service using DuckDuckGo
Enables characters to access real-time information
"""
from duckduckgo_search import DDGS
from typing import List, Dict, Optional
import asyncio
from datetime import datetime
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))
from config import settings


class SearchService:
    """Service for web searching using DuckDuckGo"""

    def __init__(self):
        self.enabled = settings.ENABLE_WEB_SEARCH
        self.max_results = settings.MAX_SEARCH_RESULTS
        self.timeout = settings.SEARCH_TIMEOUT

    async def search(
        self,
        query: str,
        max_results: Optional[int] = None,
        region: str = "wt-wt"
    ) -> List[Dict]:
        """
        Search the web using DuckDuckGo

        Args:
            query: Search query
            max_results: Maximum number of results
            region: Region code (default: worldwide)

        Returns:
            List of search results
        """
        if not self.enabled:
            return []

        max_results = max_results or self.max_results

        try:
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(
                None,
                self._search_sync,
                query,
                max_results,
                region
            )
            return results

        except Exception as e:
            print(f"Search error: {e}")
            return []

    def _search_sync(
        self,
        query: str,
        max_results: int,
        region: str
    ) -> List[Dict]:
        """Synchronous search function"""
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(
                    query,
                    region=region,
                    max_results=max_results
                ))

                formatted_results = []
                for result in results:
                    formatted_results.append({
                        "title": result.get("title", ""),
                        "url": result.get("href", ""),
                        "snippet": result.get("body", ""),
                        "source": "DuckDuckGo"
                    })

                return formatted_results

        except Exception as e:
            print(f"Search sync error: {e}")
            return []

    async def search_news(
        self,
        query: str,
        max_results: Optional[int] = None
    ) -> List[Dict]:
        """
        Search for news articles

        Args:
            query: Search query
            max_results: Maximum number of results

        Returns:
            List of news results
        """
        if not self.enabled:
            return []

        max_results = max_results or self.max_results

        try:
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(
                None,
                self._search_news_sync,
                query,
                max_results
            )
            return results

        except Exception as e:
            print(f"News search error: {e}")
            return []

    def _search_news_sync(
        self,
        query: str,
        max_results: int
    ) -> List[Dict]:
        """Synchronous news search"""
        try:
            with DDGS() as ddgs:
                results = list(ddgs.news(
                    query,
                    max_results=max_results
                ))

                formatted_results = []
                for result in results:
                    formatted_results.append({
                        "title": result.get("title", ""),
                        "url": result.get("url", ""),
                        "snippet": result.get("body", ""),
                        "date": result.get("date", ""),
                        "source": result.get("source", "DuckDuckGo News")
                    })

                return formatted_results

        except Exception as e:
            print(f"News search sync error: {e}")
            return []

    async def quick_answer(self, query: str) -> Optional[str]:
        """
        Get instant answer for simple queries

        Args:
            query: Search query

        Returns:
            Answer string if available
        """
        if not self.enabled:
            return None

        try:
            loop = asyncio.get_event_loop()
            answer = await loop.run_in_executor(
                None,
                self._quick_answer_sync,
                query
            )
            return answer

        except Exception as e:
            print(f"Quick answer error: {e}")
            return None

    def _quick_answer_sync(self, query: str) -> Optional[str]:
        """Synchronous quick answer"""
        try:
            with DDGS() as ddgs:
                results = list(ddgs.answers(query))

                if results:
                    return results[0].get("text", None)

        except:
            pass

        return None

    async def summarize_results(
        self,
        results: List[Dict],
        max_length: int = 500
    ) -> str:
        """
        Create a summary of search results

        Args:
            results: List of search results
            max_length: Maximum summary length

        Returns:
            Summary string
        """
        if not results:
            return "No results found."

        summary_parts = []

        for i, result in enumerate(results[:3], 1):
            title = result.get("title", "")
            snippet = result.get("snippet", "")

            part = f"{i}. {title}: {snippet}"
            summary_parts.append(part)

        summary = "\n".join(summary_parts)

        if len(summary) > max_length:
            summary = summary[:max_length] + "..."

        return summary

    async def search_and_summarize(
        self,
        query: str,
        max_results: Optional[int] = None
    ) -> Dict:
        """
        Search and return results with summary

        Args:
            query: Search query
            max_results: Maximum results

        Returns:
            Dict with results and summary
        """
        results = await self.search(query, max_results)
        summary = await self.summarize_results(results)

        return {
            "query": query,
            "results": results,
            "summary": summary,
            "count": len(results),
            "timestamp": datetime.utcnow().isoformat()
        }

    async def get_current_info(self, topic: str) -> str:
        """
        Get current information about a topic

        Args:
            topic: Topic to search for

        Returns:
            Information string
        """
        quick = await self.quick_answer(topic)
        if quick:
            return quick

        results = await self.search(topic, max_results=3)
        if results:
            summary = await self.summarize_results(results, max_length=300)
            return summary

        return f"I couldn't find current information about {topic}."

    async def fact_check(self, statement: str) -> Dict:
        """
        Attempt to verify a statement using web search

        Args:
            statement: Statement to check

        Returns:
            Dict with verification info
        """
        query = f"is it true that {statement}"
        results = await self.search(query, max_results=3)

        if not results:
            return {
                "statement": statement,
                "verified": False,
                "confidence": "low",
                "sources": []
            }

        return {
            "statement": statement,
            "verified": True,
            "confidence": "medium",
            "sources": [r["url"] for r in results],
            "summary": await self.summarize_results(results)
        }


search_service = SearchService()


if __name__ == "__main__":
    async def test_search():
        """Test search service"""
        print("Testing Search Service...")

        print("\nSearching for 'Python programming'...")
        results = await search_service.search("Python programming", max_results=3)

        for i, result in enumerate(results, 1):
            print(f"\n{i}. {result['title']}")
            print(f"   {result['snippet'][:100]}...")
            print(f"   {result['url']}")

        print("\n\nGetting quick answer...")
        answer = await search_service.quick_answer("what is the capital of France")
        if answer:
            print(f"Answer: {answer}")

        print("\n\nSearching and summarizing...")
        search_result = await search_service.search_and_summarize("artificial intelligence")
        print(f"Summary:\n{search_result['summary']}")

    asyncio.run(test_search())
