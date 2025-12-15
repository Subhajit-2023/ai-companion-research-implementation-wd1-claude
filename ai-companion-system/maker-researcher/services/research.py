"""
Research Service - Web search, academic papers, GitHub, ArXiv integration
"""
import asyncio
import aiohttp
from duckduckgo_search import DDGS
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import xml.etree.ElementTree as ET
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import settings


@dataclass
class SearchResult:
    title: str
    url: str
    snippet: str
    source: str
    date: Optional[str] = None
    relevance_score: float = 0.0
    metadata: Dict = field(default_factory=dict)


@dataclass
class PaperResult:
    title: str
    authors: List[str]
    abstract: str
    url: str
    source: str
    year: Optional[int] = None
    citations: int = 0
    pdf_url: Optional[str] = None
    categories: List[str] = field(default_factory=list)


@dataclass
class CodeResult:
    repo_name: str
    file_path: str
    code_snippet: str
    url: str
    language: str
    stars: int = 0
    description: str = ""


@dataclass
class ResearchSession:
    id: str
    query: str
    results: List[Any] = field(default_factory=list)
    papers: List[PaperResult] = field(default_factory=list)
    code_examples: List[CodeResult] = field(default_factory=list)
    summary: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    sources_used: List[str] = field(default_factory=list)


class ResearchService:
    def __init__(self):
        self.enabled = settings.ENABLE_WEB_SEARCH
        self.max_results = settings.MAX_SEARCH_RESULTS
        self.timeout = settings.SEARCH_TIMEOUT
        self.sessions: Dict[str, ResearchSession] = {}
        self.cache: Dict[str, Any] = {}
        self.cache_ttl = 3600

    async def search_web(
        self,
        query: str,
        max_results: Optional[int] = None,
        region: str = "wt-wt",
    ) -> List[SearchResult]:
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
            print(f"Web search error: {e}")
            return []

    def _search_duckduckgo(
        self,
        query: str,
        max_results: int,
        region: str,
    ) -> List[SearchResult]:
        try:
            with DDGS() as ddgs:
                raw_results = list(ddgs.text(
                    keywords=query,
                    region=region,
                    max_results=max_results,
                ))

                results = []
                for i, r in enumerate(raw_results):
                    results.append(SearchResult(
                        title=r.get("title", ""),
                        url=r.get("href", ""),
                        snippet=r.get("body", ""),
                        source="duckduckgo",
                        relevance_score=1.0 - (i * 0.1),
                    ))
                return results

        except Exception as e:
            print(f"DuckDuckGo error: {e}")
            return []

    async def search_news(
        self,
        query: str,
        max_results: Optional[int] = None,
    ) -> List[SearchResult]:
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
            print(f"News search error: {e}")
            return []

    def _search_news_duckduckgo(self, query: str, max_results: int) -> List[SearchResult]:
        try:
            with DDGS() as ddgs:
                raw_results = list(ddgs.news(
                    keywords=query,
                    max_results=max_results,
                ))

                results = []
                for r in raw_results:
                    results.append(SearchResult(
                        title=r.get("title", ""),
                        url=r.get("url", ""),
                        snippet=r.get("body", ""),
                        source=r.get("source", "news"),
                        date=r.get("date"),
                    ))
                return results

        except Exception as e:
            print(f"News search error: {e}")
            return []

    async def search_arxiv(
        self,
        query: str,
        max_results: int = 10,
        categories: Optional[List[str]] = None,
    ) -> List[PaperResult]:
        try:
            search_query = query.replace(" ", "+")
            if categories:
                cat_filter = "+OR+".join([f"cat:{c}" for c in categories])
                search_query = f"({search_query})+AND+({cat_filter})"

            url = f"{settings.ARXIV_API}?search_query=all:{search_query}&start=0&max_results={max_results}"

            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=self.timeout) as response:
                    if response.status != 200:
                        return []

                    content = await response.text()
                    return self._parse_arxiv_response(content)

        except Exception as e:
            print(f"ArXiv search error: {e}")
            return []

    def _parse_arxiv_response(self, xml_content: str) -> List[PaperResult]:
        papers = []
        try:
            root = ET.fromstring(xml_content)
            ns = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}

            for entry in root.findall("atom:entry", ns):
                title = entry.find("atom:title", ns)
                summary = entry.find("atom:summary", ns)
                published = entry.find("atom:published", ns)

                authors = []
                for author in entry.findall("atom:author", ns):
                    name = author.find("atom:name", ns)
                    if name is not None:
                        authors.append(name.text)

                links = entry.findall("atom:link", ns)
                pdf_url = None
                paper_url = ""
                for link in links:
                    if link.get("title") == "pdf":
                        pdf_url = link.get("href")
                    elif link.get("type") == "text/html":
                        paper_url = link.get("href")

                categories = []
                for cat in entry.findall("arxiv:primary_category", ns):
                    categories.append(cat.get("term", ""))

                year = None
                if published is not None and published.text:
                    year = int(published.text[:4])

                papers.append(PaperResult(
                    title=title.text.strip() if title is not None else "",
                    authors=authors,
                    abstract=summary.text.strip() if summary is not None else "",
                    url=paper_url,
                    source="arxiv",
                    year=year,
                    pdf_url=pdf_url,
                    categories=categories,
                ))

        except Exception as e:
            print(f"ArXiv parse error: {e}")

        return papers

    async def search_semantic_scholar(
        self,
        query: str,
        max_results: int = 10,
        fields: Optional[List[str]] = None,
    ) -> List[PaperResult]:
        try:
            fields = fields or ["title", "authors", "abstract", "url", "year", "citationCount"]
            fields_str = ",".join(fields)

            url = f"{settings.SEMANTIC_SCHOLAR_API}/paper/search"
            params = {
                "query": query,
                "limit": max_results,
                "fields": fields_str,
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=self.timeout) as response:
                    if response.status != 200:
                        return []

                    data = await response.json()
                    return self._parse_semantic_scholar_response(data)

        except Exception as e:
            print(f"Semantic Scholar error: {e}")
            return []

    def _parse_semantic_scholar_response(self, data: Dict) -> List[PaperResult]:
        papers = []
        try:
            for paper in data.get("data", []):
                authors = [a.get("name", "") for a in paper.get("authors", [])]

                papers.append(PaperResult(
                    title=paper.get("title", ""),
                    authors=authors,
                    abstract=paper.get("abstract", "") or "",
                    url=paper.get("url", ""),
                    source="semantic_scholar",
                    year=paper.get("year"),
                    citations=paper.get("citationCount", 0),
                ))

        except Exception as e:
            print(f"Semantic Scholar parse error: {e}")

        return papers

    async def search_github_code(
        self,
        query: str,
        language: Optional[str] = None,
        max_results: int = 10,
    ) -> List[CodeResult]:
        try:
            search_query = query
            if language:
                search_query += f" language:{language}"

            url = f"{settings.GITHUB_API}/search/code"
            params = {"q": search_query, "per_page": max_results}

            headers = {"Accept": "application/vnd.github.v3+json"}
            if settings.GITHUB_TOKEN:
                headers["Authorization"] = f"token {settings.GITHUB_TOKEN}"

            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, headers=headers, timeout=self.timeout) as response:
                    if response.status != 200:
                        return []

                    data = await response.json()
                    return self._parse_github_code_response(data)

        except Exception as e:
            print(f"GitHub code search error: {e}")
            return []

    def _parse_github_code_response(self, data: Dict) -> List[CodeResult]:
        results = []
        try:
            for item in data.get("items", []):
                repo = item.get("repository", {})
                results.append(CodeResult(
                    repo_name=repo.get("full_name", ""),
                    file_path=item.get("path", ""),
                    code_snippet="",
                    url=item.get("html_url", ""),
                    language=repo.get("language", ""),
                    stars=repo.get("stargazers_count", 0),
                    description=repo.get("description", "") or "",
                ))

        except Exception as e:
            print(f"GitHub parse error: {e}")

        return results

    async def search_github_repos(
        self,
        query: str,
        language: Optional[str] = None,
        max_results: int = 10,
        sort: str = "stars",
    ) -> List[Dict]:
        try:
            search_query = query
            if language:
                search_query += f" language:{language}"

            url = f"{settings.GITHUB_API}/search/repositories"
            params = {"q": search_query, "per_page": max_results, "sort": sort}

            headers = {"Accept": "application/vnd.github.v3+json"}
            if settings.GITHUB_TOKEN:
                headers["Authorization"] = f"token {settings.GITHUB_TOKEN}"

            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, headers=headers, timeout=self.timeout) as response:
                    if response.status != 200:
                        return []

                    data = await response.json()
                    repos = []
                    for item in data.get("items", []):
                        repos.append({
                            "name": item.get("full_name"),
                            "description": item.get("description"),
                            "url": item.get("html_url"),
                            "stars": item.get("stargazers_count"),
                            "language": item.get("language"),
                            "topics": item.get("topics", []),
                            "updated_at": item.get("updated_at"),
                        })
                    return repos

        except Exception as e:
            print(f"GitHub repo search error: {e}")
            return []

    async def comprehensive_research(
        self,
        query: str,
        include_papers: bool = True,
        include_code: bool = True,
        include_news: bool = False,
    ) -> ResearchSession:
        import uuid
        session_id = str(uuid.uuid4())[:8]

        session = ResearchSession(
            id=session_id,
            query=query,
        )

        tasks = [self.search_web(query)]
        sources = ["web"]

        if include_papers:
            tasks.append(self.search_arxiv(query, max_results=5))
            tasks.append(self.search_semantic_scholar(query, max_results=5))
            sources.extend(["arxiv", "semantic_scholar"])

        if include_code:
            tasks.append(self.search_github_repos(query, max_results=5))
            sources.append("github")

        if include_news:
            tasks.append(self.search_news(query, max_results=5))
            sources.append("news")

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"Research task {sources[i]} failed: {result}")
                continue

            if sources[i] == "web":
                session.results.extend(result)
            elif sources[i] in ["arxiv", "semantic_scholar"]:
                session.papers.extend(result)
            elif sources[i] == "github":
                for repo in result:
                    session.code_examples.append(CodeResult(
                        repo_name=repo.get("name", ""),
                        file_path="",
                        code_snippet="",
                        url=repo.get("url", ""),
                        language=repo.get("language", ""),
                        stars=repo.get("stars", 0),
                        description=repo.get("description", "") or "",
                    ))
            elif sources[i] == "news":
                session.results.extend(result)

        session.sources_used = sources
        self.sessions[session_id] = session
        return session

    def format_research_for_llm(self, session: ResearchSession) -> str:
        output = f"Research Results for: {session.query}\n"
        output += f"Sources used: {', '.join(session.sources_used)}\n\n"

        if session.results:
            output += "=== Web Results ===\n"
            for i, r in enumerate(session.results[:5], 1):
                output += f"{i}. {r.title}\n"
                output += f"   {r.snippet[:200]}...\n"
                output += f"   Source: {r.url}\n\n"

        if session.papers:
            output += "=== Academic Papers ===\n"
            for i, p in enumerate(session.papers[:5], 1):
                output += f"{i}. {p.title}\n"
                output += f"   Authors: {', '.join(p.authors[:3])}{'...' if len(p.authors) > 3 else ''}\n"
                output += f"   Year: {p.year or 'N/A'} | Citations: {p.citations}\n"
                output += f"   Abstract: {p.abstract[:200]}...\n"
                output += f"   URL: {p.url}\n\n"

        if session.code_examples:
            output += "=== Code Examples/Repos ===\n"
            for i, c in enumerate(session.code_examples[:5], 1):
                output += f"{i}. {c.repo_name}\n"
                output += f"   Language: {c.language} | Stars: {c.stars}\n"
                output += f"   Description: {c.description[:150]}...\n"
                output += f"   URL: {c.url}\n\n"

        return output

    def get_session(self, session_id: str) -> Optional[ResearchSession]:
        return self.sessions.get(session_id)


research_service = ResearchService()


if __name__ == "__main__":
    async def test_research():
        print("Testing Research Service...")

        print("\n1. Testing web search...")
        results = await research_service.search_web("Python asyncio tutorial", max_results=3)
        print(f"Found {len(results)} web results")
        for r in results:
            print(f"  - {r.title[:50]}...")

        print("\n2. Testing ArXiv search...")
        papers = await research_service.search_arxiv("large language models", max_results=3)
        print(f"Found {len(papers)} papers")
        for p in papers:
            print(f"  - {p.title[:50]}... ({p.year})")

        print("\n3. Testing GitHub search...")
        repos = await research_service.search_github_repos("ai companion", max_results=3)
        print(f"Found {len(repos)} repos")
        for r in repos:
            print(f"  - {r['name']} ({r['stars']} stars)")

        print("\n4. Testing comprehensive research...")
        session = await research_service.comprehensive_research(
            "Python AI chatbot optimization",
            include_papers=True,
            include_code=True,
        )
        print(f"Session {session.id} completed")
        print(f"Web results: {len(session.results)}")
        print(f"Papers: {len(session.papers)}")
        print(f"Code examples: {len(session.code_examples)}")

    asyncio.run(test_research())
