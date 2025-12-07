#!/usr/bin/env python3
# /// script
# requires-python = ">=3.8"
# dependencies = ["requests>=2.28.0"]
# ///
"""
Exa Fetch Examples - 可执行示例集

运行方式:
    uv run examples.py              # 显示帮助
    uv run examples.py concept      # 概念查询示例
    uv run examples.py tutorial     # 教程搜索示例
    uv run examples.py github       # GitHub 搜索示例
    uv run examples.py paper        # 论文搜索示例
    uv run examples.py news         # 新闻搜索示例
    uv run examples.py code         # 代码搜索示例
    uv run examples.py contents     # URL 抓取示例
    uv run examples.py all          # 运行所有示例
"""

import sys
import os

# Add scripts directory to path
script_dir = os.path.dirname(os.path.abspath(__file__))
scripts_dir = os.path.join(script_dir, "scripts")
sys.path.insert(0, scripts_dir)

from exa_fetch import (
    ExaClient, API_KEY,
    detect_intent, get_intent_config,
    format_search_results, format_contents_results
)


def check_api_key():
    """Check if API key is configured."""
    if API_KEY == "YOUR_EXA_API_KEY_HERE":
        print("ERROR: 请先在 scripts/exa_fetch.py 中配置 API_KEY")
        print("位置: scripts/exa_fetch.py:33")
        sys.exit(1)


def example_concept():
    """示例 1: 概念查询"""
    print("=" * 60)
    print("示例 1: 概念查询 - 什么是 transformer 架构")
    print("=" * 60)

    query = "什么是 transformer 架构"
    intent = detect_intent(query)
    print(f"检测到意图: {intent}")

    config = get_intent_config(intent, query)
    print(f"搜索类型: {config['search_type']}")
    print(f"结果数量: {config['num_results']}")
    print()

    client = ExaClient(API_KEY)
    result = client.search(
        query=query,
        search_type=config["search_type"],
        num_results=config["num_results"],
        contents=config.get("contents"),
    )

    output = format_search_results(result.get("results", []), query)
    print(output)


def example_tutorial():
    """示例 2: 教程搜索"""
    print("=" * 60)
    print("示例 2: 教程搜索 - Python 异步编程教程")
    print("=" * 60)

    query = "Python asyncio 教程入门"
    intent = detect_intent(query)
    print(f"检测到意图: {intent}")

    config = get_intent_config(intent, query)

    client = ExaClient(API_KEY)
    result = client.search(
        query=query,
        search_type=config["search_type"],
        num_results=config["num_results"],
        contents=config.get("contents"),
    )

    output = format_search_results(result.get("results", []), query)
    print(output)


def example_github():
    """示例 3: GitHub 仓库搜索"""
    print("=" * 60)
    print("示例 3: GitHub 搜索 - Python HTTP 客户端库")
    print("=" * 60)

    query = "Python async HTTP client library github"
    intent = detect_intent(query)
    print(f"检测到意图: {intent}")

    config = get_intent_config(intent, query)

    client = ExaClient(API_KEY)
    result = client.search(
        query=query,
        search_type=config["search_type"],
        num_results=config["num_results"],
        category=config.get("category"),
        contents=config.get("contents"),
    )

    output = format_search_results(result.get("results", []), query)
    print(output)


def example_paper():
    """示例 4: 学术论文搜索"""
    print("=" * 60)
    print("示例 4: 论文搜索 - LLM 优化技术")
    print("=" * 60)

    query = "latest LLM optimization techniques research paper"
    intent = detect_intent(query)
    print(f"检测到意图: {intent}")

    config = get_intent_config(intent, query)

    client = ExaClient(API_KEY)
    result = client.search(
        query=query,
        search_type=config["search_type"],
        num_results=config["num_results"],
        category=config.get("category"),
        include_domains=config.get("include_domains"),
        contents=config.get("contents"),
    )

    output = format_search_results(result.get("results", []), query)
    print(output)


def example_news():
    """示例 5: 新闻搜索"""
    print("=" * 60)
    print("示例 5: 新闻搜索 - AI 最新动态")
    print("=" * 60)

    query = "AI 最新新闻动态"
    intent = detect_intent(query)
    print(f"检测到意图: {intent}")

    config = get_intent_config(intent, query)

    client = ExaClient(API_KEY)
    result = client.search(
        query=query,
        search_type=config["search_type"],
        num_results=config["num_results"],
        category=config.get("category"),
        start_published_date=config.get("start_date"),
        contents=config.get("contents"),
    )

    output = format_search_results(result.get("results", []), query)
    print(output)


def example_code():
    """示例 6: 代码示例搜索"""
    print("=" * 60)
    print("示例 6: 代码搜索 - FastAPI 依赖注入示例")
    print("=" * 60)

    query = "FastAPI dependency injection 代码示例"
    intent = detect_intent(query)
    print(f"检测到意图: {intent}")

    config = get_intent_config(intent, query)

    client = ExaClient(API_KEY)
    result = client.search(
        query=query,
        search_type=config["search_type"],
        num_results=config["num_results"],
        contents=config.get("contents"),
    )

    output = format_search_results(result.get("results", []), query)
    print(output)


def example_contents():
    """示例 7: URL 内容抓取"""
    print("=" * 60)
    print("示例 7: URL 内容抓取 - Python 官方文档")
    print("=" * 60)

    urls = ["https://docs.python.org/3/library/asyncio.html"]

    client = ExaClient(API_KEY)
    result = client.get_contents(
        urls=urls,
        text=True,
        highlights={
            "numSentences": 3,
            "highlightsPerUrl": 5,
        },
        summary={"query": "Summarize the main topics covered"},
        livecrawl="fallback",
    )

    output = format_contents_results(result.get("results", []))
    print(output)


def example_intent_detection():
    """示例: 意图检测演示"""
    print("=" * 60)
    print("意图检测演示")
    print("=" * 60)

    test_queries = [
        "什么是 GraphQL",
        "Python 异步编程教程",
        "FastAPI 示例代码",
        "流行的 Python web 框架 github",
        "最新的机器学习论文",
        "OpenAI 最新新闻",
        "全面调研 AI 在医疗的应用",
        "React hooks best practices",
    ]

    print("\n查询 -> 检测到的意图\n")
    for query in test_queries:
        intent = detect_intent(query)
        print(f"  \"{query}\"")
        print(f"    -> {intent}")
        print()


def print_help():
    """Print usage help."""
    print(__doc__)
    print("\n可用示例:")
    print("  concept   - 概念查询（什么是 transformer）")
    print("  tutorial  - 教程搜索（Python asyncio 教程）")
    print("  github    - GitHub 仓库搜索")
    print("  paper     - 学术论文搜索")
    print("  news      - 新闻搜索")
    print("  code      - 代码示例搜索")
    print("  contents  - URL 内容抓取")
    print("  intent    - 意图检测演示（不调用 API）")
    print("  all       - 运行所有示例")
    print()


def main():
    if len(sys.argv) < 2:
        print_help()
        return

    cmd = sys.argv[1].lower()

    # Intent detection doesn't need API key
    if cmd == "intent":
        example_intent_detection()
        return

    if cmd == "help" or cmd == "-h" or cmd == "--help":
        print_help()
        return

    # Other examples need API key
    check_api_key()

    examples = {
        "concept": example_concept,
        "tutorial": example_tutorial,
        "github": example_github,
        "paper": example_paper,
        "news": example_news,
        "code": example_code,
        "contents": example_contents,
    }

    if cmd == "all":
        for name, func in examples.items():
            try:
                func()
                print("\n")
            except Exception as e:
                print(f"ERROR in {name}: {e}\n")
    elif cmd in examples:
        try:
            examples[cmd]()
        except Exception as e:
            print(f"ERROR: {e}")
            sys.exit(1)
    else:
        print(f"未知示例: {cmd}")
        print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
