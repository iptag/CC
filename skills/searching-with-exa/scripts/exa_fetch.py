#!/usr/bin/env python3
# /// script
# requires-python = ">=3.8"
# dependencies = ["requests>=2.28.0"]
# ///
"""
Exa Fetch - Enhanced web search and content fetching for Claude Code.
Replaces exa MCP tools with a unified CLI interface.

Usage:
    # Smart search (auto intent detection) - RECOMMENDED
    uv run exa_fetch.py smart "query" [--intent TYPE]

    # Search mode (with content fetching)
    uv run exa_fetch.py search "query" [options]

    # Contents mode (fetch specific URLs)
    uv run exa_fetch.py contents "url1" "url2" [options]

    # Code context mode (focused on code examples)
    uv run exa_fetch.py code "query" [options]

Intent types: concept, tutorial, example, github, paper, news, research, auto
"""

import sys
import json
import argparse
import requests
from typing import Optional, List, Dict, Any, Tuple
from urllib.parse import urlparse
from datetime import datetime, timedelta

# ============================================================================
# Configuration
# ============================================================================

API_KEY = ""  # Replace with your actual API key
BASE_URL = "https://api.exa.ai"
DEFAULT_NUM_RESULTS = 10
DEFAULT_SEARCH_TYPE = "deep"
DEFAULT_TIMEOUT = 60  # seconds


# ============================================================================
# Intent Detection
# ============================================================================

# Intent keywords mapping (Chinese and English)
INTENT_KEYWORDS = {
    "concept": [
        "什么是", "what is", "explain", "解释", "define", "定义",
        "介绍", "了解", "理解", "meaning of", "概念"
    ],
    "tutorial": [
        "教程", "tutorial", "guide", "how to", "如何", "怎么",
        "学习", "入门", "指南", "步骤", "learn"
    ],
    "example": [
        "示例", "example", "sample", "demo", "案例", "代码",
        "实现", "implementation", "snippet", "用法"
    ],
    "github": [
        "github", "repository", "repo", "仓库", "项目", "开源",
        "library", "框架", "framework", "package", "库"
    ],
    "paper": [
        "论文", "paper", "research", "arxiv", "研究", "学术",
        "publication", "study", "科研"
    ],
    "news": [
        "新闻", "news", "latest", "最新", "recent", "动态",
        "发布", "announcement", "更新", "trends"
    ],
    "research": [
        "调研", "research", "deep dive", "comprehensive", "全面",
        "深入", "分析", "analysis", "详细", "thorough"
    ],
}


def detect_intent(query: str) -> str:
    """
    Detect user query intent based on keywords.

    Args:
        query: User search query

    Returns:
        Intent type: concept, tutorial, example, github, paper, news, research, or auto
    """
    query_lower = query.lower()

    for intent, keywords in INTENT_KEYWORDS.items():
        if any(kw in query_lower for kw in keywords):
            return intent

    return "auto"


def get_intent_config(intent: str, query: str) -> Dict[str, Any]:
    """
    Get search configuration based on intent.

    Args:
        intent: Detected or specified intent
        query: Original search query

    Returns:
        Configuration dict with search parameters
    """
    configs = {
        "concept": {
            "search_type": "neural",
            "num_results": 10,
            "category": None,
            "include_domains": None,
            "contents": {
                "text": True,
                "livecrawl": "fallback",
                "summary": {
                    "query": "Provide a clear and comprehensive explanation of this concept"
                },
                "highlights": {
                    "numSentences": 3,
                    "highlightsPerUrl": 3,
                    "query": "key definitions and explanations"
                }
            }
        },
        "tutorial": {
            "search_type": "auto",
            "num_results": 10,
            "category": None,
            "include_domains": None,
            "contents": {
                "text": True,
                "livecrawl": "fallback",
                "highlights": {
                    "numSentences": 3,
                    "highlightsPerUrl": 5,
                    "query": "step-by-step instructions and practical examples"
                }
            }
        },
        "example": {
            "search_type": "auto",
            "num_results": 10,
            "category": None,
            "include_domains": None,
            "contents": {
                "text": True,
                "livecrawl": "fallback",
                "highlights": {
                    "numSentences": 2,
                    "highlightsPerUrl": 5,
                    "query": "code snippets and usage examples"
                }
            }
        },
        "github": {
            "search_type": "neural",
            "num_results": 10,
            "category": "github",
            "include_domains": None,
            "contents": {
                "text": True,
                "livecrawl": "fallback",
                "summary": {
                    "query": "What is this repository about and what are its main features?"
                }
            }
        },
        "paper": {
            "search_type": "neural",
            "num_results": 10,
            "category": "research paper",
            "include_domains": ["arxiv.org", "paperswithcode.com"],
            "contents": {
                "text": True,
                "livecrawl": "fallback",
                "summary": {
                    "query": "Summarize the research problem, methodology, and key findings"
                }
            }
        },
        "news": {
            "search_type": "auto",
            "num_results": 10,
            "category": "news",
            "include_domains": None,
            "start_date": (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%dT00:00:00.000Z"),
            "contents": {
                "text": True,
                "livecrawl": "fallback",
                "highlights": {
                    "numSentences": 2,
                    "highlightsPerUrl": 3
                }
            }
        },
        "research": {
            "search_type": "deep",
            "num_results": 15,
            "category": None,
            "include_domains": None,
            "contents": {
                "text": True,
                "livecrawl": "fallback",
                "summary": {
                    "query": "Provide a comprehensive overview of this topic"
                },
                "highlights": {
                    "numSentences": 3,
                    "highlightsPerUrl": 5,
                    "query": query
                }
            }
        },
        "auto": {
            "search_type": "deep",
            "num_results": 10,
            "category": None,
            "include_domains": None,
            "contents": {
                "text": True,
                "livecrawl": "fallback",
                "highlights": {
                    "numSentences": 3,
                    "highlightsPerUrl": 3,
                    "query": query
                },
                "summary": {
                    "query": f"Summarize the key points about: {query}"
                }
            }
        }
    }

    return configs.get(intent, configs["auto"])


# ============================================================================
# API Client
# ============================================================================

class ExaClient:
    """Minimal Exa API client."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "x-api-key": api_key,
            "Content-Type": "application/json"
        }

    def search(
        self,
        query: str,
        search_type: str = DEFAULT_SEARCH_TYPE,
        num_results: int = DEFAULT_NUM_RESULTS,
        category: Optional[str] = None,
        include_domains: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None,
        start_published_date: Optional[str] = None,
        contents: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Execute search with optional content fetching."""
        payload = {
            "query": query,
            "type": search_type,
            "numResults": num_results,
        }

        if category:
            payload["category"] = category
        if include_domains:
            payload["includeDomains"] = include_domains
        if exclude_domains:
            payload["excludeDomains"] = exclude_domains
        if start_published_date:
            payload["startPublishedDate"] = start_published_date
        if contents:
            payload["contents"] = contents

        response = requests.post(
            f"{BASE_URL}/search",
            json=payload,
            headers=self.headers,
            timeout=DEFAULT_TIMEOUT
        )
        response.raise_for_status()
        return response.json()

    def get_contents(
        self,
        urls: List[str],
        text: bool = True,
        highlights: Optional[Dict[str, Any]] = None,
        summary: Optional[Dict[str, Any]] = None,
        livecrawl: str = "fallback",
    ) -> Dict[str, Any]:
        """Fetch content from URLs."""
        payload = {
            "urls": urls,
            "livecrawl": livecrawl,
        }

        if text:
            payload["text"] = True
        if highlights:
            payload["highlights"] = highlights
        if summary:
            payload["summary"] = summary

        response = requests.post(
            f"{BASE_URL}/contents",
            json=payload,
            headers=self.headers,
            timeout=DEFAULT_TIMEOUT
        )
        response.raise_for_status()
        return response.json()


# ============================================================================
# Output Formatting
# ============================================================================

def extract_domain(url: str) -> str:
    """Extract domain from URL."""
    try:
        parsed = urlparse(url)
        return parsed.netloc or url
    except Exception:
        return url


def format_date(date_str: Optional[str]) -> str:
    """Format date string for display."""
    if not date_str:
        return "N/A"
    try:
        # Handle ISO format
        if "T" in date_str:
            dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            return dt.strftime("%Y-%m-%d")
        return date_str[:10]  # YYYY-MM-DD
    except Exception:
        return date_str[:10] if len(date_str) >= 10 else date_str


def format_search_results(results: List[Dict], query: str) -> str:
    """Format search results as Markdown."""
    if not results:
        return f"## 搜索结果: \"{query}\"\n\n未找到相关结果。"

    lines = [f"## 搜索结果: \"{query}\"", ""]

    for i, item in enumerate(results, 1):
        title = item.get("title", "无标题")
        url = item.get("url", "")
        domain = extract_domain(url)
        date = format_date(item.get("publishedDate"))
        summary = item.get("summary", "")
        highlights = item.get("highlights", [])
        text = item.get("text", "")

        lines.append(f"### {i}. [{title}]({url})")
        lines.append(f"**来源**: {domain} | **日期**: {date}")
        lines.append("")

        # Summary
        if summary:
            lines.append(f"**摘要**: {summary}")
            lines.append("")

        # Highlights
        if highlights:
            lines.append("**关键内容**:")
            for h in highlights[:3]:  # Limit to 3 highlights
                # Clean and truncate highlight
                h_clean = h.strip().replace("\n", " ")
                if len(h_clean) > 300:
                    h_clean = h_clean[:300] + "..."
                lines.append(f"> {h_clean}")
            lines.append("")

        # Text snippet if no highlights or summary
        if not highlights and not summary and text:
            snippet = text[:500].strip().replace("\n", " ")
            if len(text) > 500:
                snippet += "..."
            lines.append(f"**内容预览**: {snippet}")
            lines.append("")

        lines.append("---")
        lines.append("")

    return "\n".join(lines)


def format_contents_results(results: List[Dict]) -> str:
    """Format content fetch results as Markdown."""
    if not results:
        return "## 内容抓取结果\n\n未获取到内容。"

    lines = ["## 内容抓取结果", ""]

    for i, item in enumerate(results, 1):
        title = item.get("title", "无标题")
        url = item.get("url", "")
        domain = extract_domain(url)
        summary = item.get("summary", "")
        highlights = item.get("highlights", [])
        text = item.get("text", "")

        lines.append(f"### {i}. [{title}]({url})")
        lines.append(f"**来源**: {domain}")
        lines.append("")

        if summary:
            lines.append(f"**摘要**: {summary}")
            lines.append("")

        if highlights:
            lines.append("**关键内容**:")
            for h in highlights[:5]:
                h_clean = h.strip().replace("\n", " ")
                if len(h_clean) > 300:
                    h_clean = h_clean[:300] + "..."
                lines.append(f"> {h_clean}")
            lines.append("")

        if text:
            # Show more text for contents mode
            snippet = text[:1000].strip()
            if len(text) > 1000:
                snippet += "..."
            lines.append(f"**内容**:\n```\n{snippet}\n```")
            lines.append("")

        lines.append("---")
        lines.append("")

    return "\n".join(lines)


# ============================================================================
# Commands
# ============================================================================

def cmd_search(args: argparse.Namespace) -> int:
    """Execute search command."""
    client = ExaClient(API_KEY)

    # Build contents options
    contents = None
    if not args.no_contents:
        contents = {
            "text": True,
            "livecrawl": "fallback",
        }
        if args.highlights:
            contents["highlights"] = {
                "numSentences": 3,
                "highlightsPerUrl": 3,
                "query": args.query
            }
        if args.summary:
            contents["summary"] = {
                "query": f"Summarize the key points about: {args.query}"
            }

    # Parse domains
    include_domains = None
    if args.include_domains:
        include_domains = [d.strip() for d in args.include_domains.split(",")]

    exclude_domains = None
    if args.exclude_domains:
        exclude_domains = [d.strip() for d in args.exclude_domains.split(",")]

    try:
        result = client.search(
            query=args.query,
            search_type=args.type,
            num_results=args.num_results,
            category=args.category,
            include_domains=include_domains,
            exclude_domains=exclude_domains,
            start_published_date=args.start_date,
            contents=contents,
        )

        output = format_search_results(result.get("results", []), args.query)
        print(output)
        return 0

    except requests.exceptions.HTTPError as e:
        print(f"ERROR: API request failed: {e}", file=sys.stderr)
        return 1
    except requests.exceptions.Timeout:
        print("ERROR: Request timeout", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


def cmd_contents(args: argparse.Namespace) -> int:
    """Execute contents command."""
    client = ExaClient(API_KEY)

    highlights = None
    if args.highlights:
        highlights = {
            "numSentences": 3,
            "highlightsPerUrl": 5,
        }

    summary = None
    if args.summary:
        summary = {"query": "Summarize the main points"}

    try:
        result = client.get_contents(
            urls=args.urls,
            text=True,
            highlights=highlights,
            summary=summary,
            livecrawl=args.livecrawl,
        )

        output = format_contents_results(result.get("results", []))
        print(output)
        return 0

    except requests.exceptions.HTTPError as e:
        print(f"ERROR: API request failed: {e}", file=sys.stderr)
        return 1
    except requests.exceptions.Timeout:
        print("ERROR: Request timeout", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


def cmd_code(args: argparse.Namespace) -> int:
    """Execute code context search command."""
    client = ExaClient(API_KEY)

    # Code-focused search: prioritize github and technical sites
    include_domains = ["github.com", "stackoverflow.com", "dev.to", "medium.com"]
    if args.include_domains:
        include_domains = [d.strip() for d in args.include_domains.split(",")]

    contents = {
        "text": True,
        "livecrawl": "fallback",
        "highlights": {
            "numSentences": 5,
            "highlightsPerUrl": 5,
            "query": f"code examples and implementation for: {args.query}"
        }
    }

    try:
        result = client.search(
            query=args.query,
            search_type="deep",
            num_results=args.num_results,
            category=args.category or "github",
            include_domains=include_domains if not args.category else None,
            contents=contents,
        )

        output = format_search_results(result.get("results", []), args.query)
        print(output)
        return 0

    except requests.exceptions.HTTPError as e:
        print(f"ERROR: API request failed: {e}", file=sys.stderr)
        return 1
    except requests.exceptions.Timeout:
        print("ERROR: Request timeout", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


def cmd_smart(args: argparse.Namespace) -> int:
    """Execute smart search with automatic intent detection."""
    client = ExaClient(API_KEY)

    # Detect or use specified intent
    if args.intent == "auto":
        intent = detect_intent(args.query)
        print(f"[检测到意图: {intent}]", file=sys.stderr)
    else:
        intent = args.intent

    # Get intent-based configuration
    config = get_intent_config(intent, args.query)

    # Override with user-specified values
    num_results = args.num_results if args.num_results else config["num_results"]

    try:
        result = client.search(
            query=args.query,
            search_type=config["search_type"],
            num_results=num_results,
            category=config.get("category"),
            include_domains=config.get("include_domains"),
            start_published_date=config.get("start_date"),
            contents=config.get("contents"),
        )

        output = format_search_results(result.get("results", []), args.query)
        print(output)
        return 0

    except requests.exceptions.HTTPError as e:
        print(f"ERROR: API request failed: {e}", file=sys.stderr)
        return 1
    except requests.exceptions.Timeout:
        print("ERROR: Request timeout", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


# ============================================================================
# Main
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Exa Fetch - Enhanced web search and content fetching",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Search command
    search_parser = subparsers.add_parser(
        "search",
        help="Search the web with optional content fetching"
    )
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument(
        "--num-results", "-n",
        type=int,
        default=DEFAULT_NUM_RESULTS,
        help=f"Number of results (default: {DEFAULT_NUM_RESULTS})"
    )
    search_parser.add_argument(
        "--type", "-t",
        choices=["auto", "neural", "deep", "fast"],
        default=DEFAULT_SEARCH_TYPE,
        help=f"Search type (default: {DEFAULT_SEARCH_TYPE})"
    )
    search_parser.add_argument(
        "--category", "-c",
        choices=["github", "research paper", "news", "company", "pdf", "tweet"],
        help="Filter by category"
    )
    search_parser.add_argument(
        "--include-domains",
        help="Comma-separated list of domains to include"
    )
    search_parser.add_argument(
        "--exclude-domains",
        help="Comma-separated list of domains to exclude"
    )
    search_parser.add_argument(
        "--start-date",
        help="Only results after this date (ISO format: 2024-01-01)"
    )
    search_parser.add_argument(
        "--no-contents",
        action="store_true",
        help="Skip content fetching (faster, less detail)"
    )
    search_parser.add_argument(
        "--no-highlights",
        action="store_false",
        dest="highlights",
        help="Disable highlights extraction"
    )
    search_parser.add_argument(
        "--no-summary",
        action="store_false",
        dest="summary",
        help="Disable summary generation"
    )
    search_parser.set_defaults(func=cmd_search, highlights=True, summary=True)

    # Contents command
    contents_parser = subparsers.add_parser(
        "contents",
        help="Fetch content from specific URLs"
    )
    contents_parser.add_argument(
        "urls",
        nargs="+",
        help="URLs to fetch"
    )
    contents_parser.add_argument(
        "--livecrawl",
        choices=["never", "fallback", "always", "preferred"],
        default="fallback",
        help="Live crawl mode (default: fallback)"
    )
    contents_parser.add_argument(
        "--no-highlights",
        action="store_false",
        dest="highlights",
        help="Disable highlights extraction"
    )
    contents_parser.add_argument(
        "--no-summary",
        action="store_false",
        dest="summary",
        help="Disable summary generation"
    )
    contents_parser.set_defaults(func=cmd_contents, highlights=True, summary=True)

    # Code command
    code_parser = subparsers.add_parser(
        "code",
        help="Search for code examples and implementations"
    )
    code_parser.add_argument("query", help="Code search query")
    code_parser.add_argument(
        "--num-results", "-n",
        type=int,
        default=DEFAULT_NUM_RESULTS,
        help=f"Number of results (default: {DEFAULT_NUM_RESULTS})"
    )
    code_parser.add_argument(
        "--category", "-c",
        choices=["github", "research paper", "pdf"],
        help="Override default github category"
    )
    code_parser.add_argument(
        "--include-domains",
        help="Override default code-focused domains"
    )
    code_parser.set_defaults(func=cmd_code)

    # Smart command (auto intent detection)
    smart_parser = subparsers.add_parser(
        "smart",
        help="Smart search with automatic intent detection"
    )
    smart_parser.add_argument("query", help="Search query (intent auto-detected)")
    smart_parser.add_argument(
        "--intent", "-i",
        choices=["auto", "concept", "tutorial", "example", "github", "paper", "news", "research"],
        default="auto",
        help="Override auto-detected intent"
    )
    smart_parser.add_argument(
        "--num-results", "-n",
        type=int,
        default=None,
        help="Number of results (default: intent-based)"
    )
    smart_parser.set_defaults(func=cmd_smart)

    args = parser.parse_args()

    if API_KEY == "YOUR_EXA_API_KEY_HERE":
        print("ERROR: Please set your EXA API key in the script", file=sys.stderr)
        sys.exit(1)

    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
