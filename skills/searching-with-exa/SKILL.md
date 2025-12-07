---
name: searching-with-exa
description: Exa AI neural search for docs, code, GitHub repos, papers. Triggers on "搜索/查询/查找/找一下", "有没有...文档/示例", "如何实现", "最新的...". Use instead of WebFetch when needing multiple results or smart filtering.
---

# Exa Fetch - 增强版网页搜索与内容抓取

## Overview

基于 Exa AI 的智能搜索工具，作为 WebFetch 的增强版本，提供：
- **智能意图识别** - 自动检测查询意图，优化搜索参数
- 深度语义搜索（neural/deep 模式）
- 自动内容抓取与摘要
- 代码示例专项搜索
- 类别过滤（GitHub、论文、新闻等）

## When to Use This Skill

使用此 skill 当用户需要：
- 查找技术文档、API 文档、框架用法
- 搜索代码示例、最佳实践、实现参考
- 查找 GitHub 仓库、开源项目
- 获取研究论文、技术文章
- WebFetch 返回内容不充分时
- 需要多个高质量搜索结果时
- 搜索特定类型内容（论文、新闻、公司信息）

## Commands

### 0. smart - 智能搜索（推荐）

自动识别用户意图，选择最佳搜索参数。

```bash
uv run ~/.claude/skills/searching-with-exa/scripts/exa_fetch.py smart "query" [--intent TYPE]
```

**参数**:
- `query` (必需): 搜索查询（自动识别意图）
- `--intent, -i`: 手动指定意图类型（可选）
- `--num-results, -n`: 结果数量（默认: 根据意图自动调整）

**意图类型**:

| 意图 | 触发词 | 说明 |
|------|--------|------|
| `concept` | 什么是、explain、解释、定义 | 概念解释，提取清晰定义 |
| `tutorial` | 教程、how to、如何、指南 | 教程查找，提取步骤和示例 |
| `example` | 示例、example、demo、代码 | 代码示例，提取代码片段 |
| `github` | github、仓库、项目、框架 | GitHub 仓库，提取项目特性 |
| `paper` | 论文、paper、arxiv、研究 | 学术论文，提取方法和结论 |
| `news` | 新闻、latest、最新、动态 | 最新新闻（7天内） |
| `research` | 调研、deep dive、全面、分析 | 深度研究，全面探索 |
| `auto` | （默认） | 自动检测意图 |

**示例**:
```bash
# 自动检测意图
uv run ~/.claude/skills/searching-with-exa/scripts/exa_fetch.py smart "什么是 transformer 架构"
# [检测到意图: concept]

# 手动指定意图
uv run ~/.claude/skills/searching-with-exa/scripts/exa_fetch.py smart "React hooks" --intent tutorial

# 查找论文
uv run ~/.claude/skills/searching-with-exa/scripts/exa_fetch.py smart "最新的 LLM 优化论文"
# [检测到意图: paper]
```

### 1. search - 智能搜索（默认模式）

搜索网页并自动抓取内容、生成摘要。

```bash
uv run ~/.claude/skills/searching-with-exa/scripts/exa_fetch.py search "query" [options]
```

**参数**:
- `query` (必需): 搜索查询
- `--num-results, -n`: 结果数量（默认: 10）
- `--type, -t`: 搜索类型 `auto|neural|deep|fast`（默认: deep）
- `--category, -c`: 类别过滤 `github|research paper|news|company|pdf|tweet`
- `--include-domains`: 域名白名单（逗号分隔）
- `--exclude-domains`: 域名黑名单（逗号分隔）
- `--start-date`: 起始日期（ISO 格式: 2024-01-01）
- `--no-contents`: 仅搜索不抓取内容（更快）
- `--no-highlights`: 禁用高亮提取
- `--no-summary`: 禁用摘要生成

**示例**:
```bash
# 基础搜索
uv run ~/.claude/skills/searching-with-exa/scripts/exa_fetch.py search "React hooks best practices"

# 限定 GitHub
uv run ~/.claude/skills/searching-with-exa/scripts/exa_fetch.py search "Python async HTTP client" -c github

# 搜索最新论文
uv run ~/.claude/skills/searching-with-exa/scripts/exa_fetch.py search "transformer attention mechanism" -c "research paper" --start-date 2024-01-01

# 限定特定域名
uv run ~/.claude/skills/searching-with-exa/scripts/exa_fetch.py search "Next.js app router" --include-domains "nextjs.org,vercel.com"
```

### 2. code - 代码上下文搜索

专注于代码示例和实现，默认搜索 GitHub、StackOverflow 等技术站点。

```bash
uv run ~/.claude/skills/searching-with-exa/scripts/exa_fetch.py code "query" [options]
```

**参数**:
- `query` (必需): 代码相关查询
- `--num-results, -n`: 结果数量（默认: 10）
- `--category, -c`: 覆盖默认 github 类别
- `--include-domains`: 覆盖默认代码站点

**示例**:
```bash
# 搜索实现示例
uv run ~/.claude/skills/searching-with-exa/scripts/exa_fetch.py code "Python websocket client example"

# 搜索特定库用法
uv run ~/.claude/skills/searching-with-exa/scripts/exa_fetch.py code "FastAPI dependency injection"

# 搜索算法实现
uv run ~/.claude/skills/searching-with-exa/scripts/exa_fetch.py code "LRU cache implementation Python"
```

### 3. contents - URL 内容抓取

直接获取指定 URL 的内容，支持实时抓取。

```bash
uv run ~/.claude/skills/searching-with-exa/scripts/exa_fetch.py contents "url1" "url2" [options]
```

**参数**:
- `urls` (必需): 一个或多个 URL
- `--livecrawl`: 抓取模式 `never|fallback|always|preferred`（默认: fallback）
- `--no-highlights`: 禁用高亮提取
- `--no-summary`: 禁用摘要生成

**示例**:
```bash
# 抓取单个页面
uv run ~/.claude/skills/searching-with-exa/scripts/exa_fetch.py contents "https://docs.python.org/3/library/asyncio.html"

# 抓取多个页面
uv run ~/.claude/skills/searching-with-exa/scripts/exa_fetch.py contents \
    "https://react.dev/learn" \
    "https://nextjs.org/docs" \
    --livecrawl preferred
```

## Output Format

输出为 Markdown 格式，包含：
- 标题（带链接）
- 来源域名和日期
- 摘要
- 关键内容高亮
- 内容预览

```markdown
## 搜索结果: "query"

### 1. [标题](url)
**来源**: domain.com | **日期**: 2025-01-15

**摘要**: 简要描述...

**关键内容**:
> 高亮片段 1
> 高亮片段 2

---
```

## Quick Reference

- **代码搜索** → `code` 命令（默认 GitHub）
- **已知 URL** → `contents` 命令
- **其他** → `smart` 或 `search` 命令

详细的决策树、类别说明和故障排查请参阅 [REFERENCE.md](REFERENCE.md#决策树)。

## Examples

### 示例 1: 查找框架文档

**用户**: "帮我找一下 FastAPI 的依赖注入文档"

```bash
uv run ~/.claude/skills/searching-with-exa/scripts/exa_fetch.py search "FastAPI dependency injection documentation" --include-domains "fastapi.tiangolo.com"
```

### 示例 2: 搜索开源项目

**用户**: "有没有 Python 的异步 HTTP 客户端库推荐"

```bash
uv run ~/.claude/skills/searching-with-exa/scripts/exa_fetch.py search "Python async HTTP client library" -c github -n 8
```

### 示例 3: 获取最新研究

**用户**: "最新的大语言模型优化论文"

```bash
uv run ~/.claude/skills/searching-with-exa/scripts/exa_fetch.py search "LLM optimization techniques 2024" -c "research paper" --start-date 2024-06-01
```

### 示例 4: 代码实现参考

**用户**: "如何实现 Python 的 LRU 缓存"

```bash
uv run ~/.claude/skills/searching-with-exa/scripts/exa_fetch.py code "LRU cache implementation Python example"
```

### 示例 5: 抓取特定页面

**用户**: "帮我看一下这个页面的内容 https://docs.python.org/3/library/asyncio.html"

```bash
uv run ~/.claude/skills/searching-with-exa/scripts/exa_fetch.py contents "https://docs.python.org/3/library/asyncio.html" --livecrawl preferred
```

### 示例 6: 技术新闻

**用户**: "搜索一下 OpenAI 最近的动态"

```bash
uv run ~/.claude/skills/searching-with-exa/scripts/exa_fetch.py search "OpenAI announcements" -c news --start-date 2024-11-01
```

## Reference

详细的 API 参数说明和响应格式，请参阅 [REFERENCE.md](REFERENCE.md)。
