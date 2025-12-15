"""
Web Search Service using DuckDuckGo
Enables AI companions to access real-time internet information
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
    """Service for web search using DuckDuckGo"""

    def __init__(self):
        self.provider = settings.SEARCH_PROVIDER
        self.max_results = settings.MAX_SEARCH_RESULTS
        self.timeout = settings.SEARCH_TIMEOUT
        self.enabled = settings.ENABLE_WEB_SEARCH

    async def search(
        self,
        query: str,
        max_results: Optional[int] = None,
        region: str = "wt-wt",
    ) -> List[Dict]:
        """
        Perform web search

        Args:
            query: Search query
            max_results: Maximum number of results
            region: Region code (wt-wt for worldwide)

        Returns:
            List of search results
        """
        if not self.enabled:
            return []

        max_results = max_results or self.max_results

        try:
            results = await asyncio.to_thread(
                self._search_duckduckgo,
                query,
                max_results,
                region,
            )
            return results

        except Exception as e:
            print(f"Error performing search: {e}")
            return []

    def _search_duckduckgo(
        self,
        query: str,
        max_results: int,
        region: str,
    ) -> List[Dict]:
        """Perform DuckDuckGo search (synchronous)"""
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(
                    keywords=query,
                    region=region,
                    max_results=max_results,
                ))

                formatted_results = []
                for i, result in enumerate(results):
                    formatted_results.append({
                        "position": i + 1,
                        "title": result.get("title", ""),
                        "url": result.get("href", ""),
                        "snippet": result.get("body", ""),
                        "source": "duckduckgo",
                    })

                return formatted_results

        except Exception as e:
            print(f"DuckDuckGo search error: {e}")
            return []

    async def search_news(
        self,
        query: str,
        max_results: Optional[int] = None,
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
            results = await asyncio.to_thread(
                self._search_news_duckduckgo,
                query,
                max_results,
            )
            return results

        except Exception as e:
            print(f"Error searching news: {e}")
            return []

    def _search_news_duckduckgo(self, query: str, max_results: int) -> List[Dict]:
        """Perform DuckDuckGo news search (synchronous)"""
        try:
            with DDGS() as ddgs:
                results = list(ddgs.news(
                    keywords=query,
                    max_results=max_results,
                ))

                formatted_results = []
                for i, result in enumerate(results):
                    formatted_results.append({
                        "position": i + 1,
                        "title": result.get("title", ""),
                        "url": result.get("url", ""),
                        "snippet": result.get("body", ""),
                        "date": result.get("date", ""),
                        "source": result.get("source", ""),
                    })

                return formatted_results

        except Exception as e:
            print(f"DuckDuckGo news search error: {e}")
            return []

    async def quick_answer(self, query: str) -> Optional[str]:
        """
        Get quick answer/instant answer for a query

        Args:
            query: Search query

        Returns:
            Quick answer text or None
        """
        if not self.enabled:
            return None

        try:
            answer = await asyncio.to_thread(
                self._get_instant_answer,
                query,
            )
            return answer

        except Exception as e:
            print(f"Error getting quick answer: {e}")
            return None

    def _get_instant_answer(self, query: str) -> Optional[str]:
        """Get instant answer from DuckDuckGo (synchronous)"""
        try:
            with DDGS() as ddgs:
                results = list(ddgs.answers(keywords=query))

                if results:
                    return results[0].get("text", None)

                return None

        except Exception as e:
            print(f"Instant answer error: {e}")
            return None

    async def format_search_results_for_llm(
        self,
        results: List[Dict],
        query: str,
    ) -> str:
        """
        Format search results for inclusion in LLM context

        Args:
            results: Search results
            query: Original query

        Returns:
            Formatted text for LLM
        """
        if not results:
            return f"No search results found for: {query}"

        formatted = f"Search results for '{query}':\n\n"

        for i, result in enumerate(results, 1):
            formatted += f"{i}. {result['title']}\n"
            formatted += f"   {result['snippet']}\n"
            formatted += f"   Source: {result['url']}\n\n"

        formatted += "\nYou can use this information to answer the user's question with up-to-date facts."

        return formatted

    async def should_search(self, message: str, llm_service) -> bool:
        """
        Determine if a web search would be helpful for answering the message

        Args:
            message: User message
            llm_service: LLM service instance

        Returns:
            True if search would be helpful
        """
        search_indicators = [
            "what is",
            "who is",
            "when did",
            "where is",
            "how to",
            "search for",
            "look up",
            "find out",
            "tell me about",
            "latest",
            "current",
            "news",
            "recent",
            "today",
            "now",
        ]

        message_lower = message.lower()
        return any(indicator in message_lower for indicator in search_indicators)

    async def extract_search_query(self, message: str, llm_service) -> str:
        """
        Extract optimal search query from user message using LLM

        Args:
            message: User message
            llm_service: LLM service instance

        Returns:
            Optimized search query
        """
        try:
            prompt = f"""Extract a concise search query from this message:

"{message}"

Return only the search query, no explanations. Make it short and specific.

Query:"""

            response = await llm_service.generate_response(
                messages=[{"role": "user", "content": prompt}],
                character_info={"persona_type": "default", "name": "AI"},
                stream=False,
            )

            query = response["content"].strip().strip('"').strip("'")
            return query

        except Exception as e:
            print(f"Error extracting search query: {e}")
            return message[:100]


search_service = SearchService()


if __name__ == "__main__":
    async def test_search_service():
        """Test search service"""
        print("Testing Search Service...")

        if not search_service.enabled:
            print("Web search is disabled in settings")
            return

        print("\n1. Testing web search...")
        results = await search_service.search("Python programming", max_results=3)

        print(f"Found {len(results)} results:")
        for result in results:
            print(f"\n{result['position']}. {result['title']}")
            print(f"   {result['url']}")
            print(f"   {result['snippet'][:100]}...")

        print("\n2. Testing news search...")
        news_results = await search_service.search_news("artificial intelligence", max_results=3)

        print(f"Found {len(news_results)} news articles:")
        for article in news_results:
            print(f"\n{article['position']}. {article['title']}")
            print(f"   {article['source']} - {article['date']}")

        print("\n3. Testing quick answer...")
        answer = await search_service.quick_answer("What is Python programming language?")

        if answer:
            print(f"Quick answer: {answer}")
        else:
            print("No quick answer available")

        print("\n4. Testing result formatting...")
        formatted = await search_service.format_search_results_for_llm(
            results[:2],
            "Python programming"
        )
        print("Formatted for LLM:")
        print(formatted[:300] + "...")

    asyncio.run(test_search_service())
