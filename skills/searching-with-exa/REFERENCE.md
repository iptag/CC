# Exa Fetch API Reference

完整的 Exa API 参数说明和响应格式参考。

## API 概述

Exa Fetch 封装了 Exa AI 的两个核心 API：
- **Search API** (`/search`) - 智能语义搜索
- **Contents API** (`/contents`) - URL 内容抓取

官方文档：
- Search API: https://docs.exa.ai/reference/search
- Contents API: https://docs.exa.ai/reference/get-contents

---

## Search API 参数

### 基础参数

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| `query` | string | ✅ | - | 搜索查询字符串 |
| `type` | string | - | `deep` | 搜索类型 |
| `numResults` | int | - | 10 | 返回结果数量（最多100） |

### 搜索类型 (`type`)

| 值 | 说明 | 适用场景 |
|----|------|----------|
| `neural` | 基于嵌入的语义搜索 | 概念性查询、相似内容 |
| `auto` | 智能组合多种方法 | 通用搜索 |
| `fast` | 简化搜索模型 | 需要快速响应 |
| `deep` | 全面搜索 + 查询扩展 | 需要详细结果（默认） |

### 类别过滤 (`category`)

| 值 | 说明 | 示例查询 |
|----|------|----------|
| `github` | GitHub 仓库 | "Python HTTP client library" |
| `research paper` | 学术论文 | "transformer attention mechanism" |
| `news` | 新闻资讯 | "OpenAI latest announcement" |
| `company` | 公司信息 | "Anthropic company overview" |
| `pdf` | PDF 文档 | "machine learning textbook" |
| `tweet` | Twitter 内容 | "AI community reactions" |
| `personal site` | 个人网站/博客 | "developer blog posts" |
| `linkedin profile` | LinkedIn 资料 | "AI researcher profiles" |
| `financial report` | 财务报告 | "tech company earnings" |

### 域名过滤

| 参数 | 类型 | 说明 |
|------|------|------|
| `includeDomains` | string[] | 仅包含这些域名（最多1200个） |
| `excludeDomains` | string[] | 排除这些域名（最多1200个） |

**示例**：
```python
include_domains = ["github.com", "stackoverflow.com", "docs.python.org"]
exclude_domains = ["pinterest.com", "facebook.com"]
```

### 日期过滤

| 参数 | 格式 | 说明 |
|------|------|------|
| `startCrawlDate` | ISO 8601 | 返回此日期后抓取的结果 |
| `endCrawlDate` | ISO 8601 | 返回此日期前抓取的结果 |
| `startPublishedDate` | ISO 8601 | 返回此日期后发布的结果 |
| `endPublishedDate` | ISO 8601 | 返回此日期前发布的结果 |

**格式示例**：`2024-01-01T00:00:00.000Z`

### 文本过滤

| 参数 | 类型 | 说明 |
|------|------|------|
| `includeText` | string[] | 必须包含的文本（1个字符串，最多5词） |
| `excludeText` | string[] | 不能包含的文本（1个字符串，最多5词） |

### 内容选项 (`contents`)

控制是否在搜索结果中包含页面内容。

```python
contents = {
    "text": True,                    # 返回完整页面文本
    "highlights": {
        "numSentences": 3,           # 每个高亮的句子数
        "highlightsPerUrl": 3,       # 每个结果的高亮数
        "query": "custom query"      # 自定义高亮查询
    },
    "summary": {
        "query": "summarize key points"  # 摘要生成提示
    },
    "livecrawl": "fallback",         # 实时抓取模式
    "livecrawlTimeout": 10000        # 超时（毫秒）
}
```

#### 实时抓取模式 (`livecrawl`)

| 值 | 说明 |
|----|------|
| `never` | 禁用实时抓取 |
| `fallback` | 缓存为空时实时抓取（默认） |
| `always` | 始终实时抓取 |
| `preferred` | 优先实时抓取，失败用缓存 |

---

## Contents API 参数

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| `urls` | string[] | ✅ | - | 要抓取的 URL 列表 |
| `text` | bool | - | true | 返回页面文本 |
| `highlights` | object | - | - | 高亮提取配置 |
| `summary` | object | - | - | 摘要生成配置 |
| `livecrawl` | string | - | `fallback` | 实时抓取模式 |
| `livecrawlTimeout` | int | - | 10000 | 超时毫秒数 |
| `subpages` | int | - | 0 | 抓取的子页面数量 |
| `subpageTarget` | string/string[] | - | - | 子页面搜索关键词 |

---

## 响应格式

### Search 响应

```json
{
    "requestId": "uuid-string",
    "resolvedSearchType": "deep",
    "results": [
        {
            "title": "页面标题",
            "url": "https://example.com/page",
            "publishedDate": "2024-01-15",
            "author": "作者名",
            "id": "doc-id",
            "image": "https://example.com/image.jpg",
            "favicon": "https://example.com/favicon.ico",
            "text": "完整页面文本...",
            "highlights": ["高亮片段1", "高亮片段2"],
            "highlightScores": [0.95, 0.87],
            "summary": "页面摘要..."
        }
    ],
    "costDollars": {
        "total": 0.005,
        "search": 0.002,
        "contents": 0.003
    }
}
```

### Contents 响应

```json
{
    "requestId": "uuid-string",
    "results": [
        {
            "url": "https://example.com/page",
            "title": "页面标题",
            "text": "完整页面文本...",
            "highlights": ["高亮片段1", "高亮片段2"],
            "summary": "页面摘要...",
            "author": "作者名",
            "publishedDate": "2024-01-15",
            "image": "https://example.com/image.jpg"
        }
    ],
    "statuses": [
        {"url": "https://example.com/page", "status": "success"}
    ],
    "costDollars": {
        "total": 0.003
    }
}
```

---

## CLI 命令对照

### search 命令

```bash
uv run ~/.claude/skills/searching-with-exa/scripts/exa_fetch.py search "query" [options]
```

| CLI 参数 | API 参数 | 说明 |
|----------|----------|------|
| `query` | `query` | 搜索查询 |
| `-n, --num-results` | `numResults` | 结果数量 |
| `-t, --type` | `type` | 搜索类型 |
| `-c, --category` | `category` | 类别过滤 |
| `--include-domains` | `includeDomains` | 域名白名单 |
| `--exclude-domains` | `excludeDomains` | 域名黑名单 |
| `--start-date` | `startPublishedDate` | 起始日期 |
| `--no-contents` | - | 禁用内容抓取 |
| `--no-highlights` | - | 禁用高亮 |
| `--no-summary` | - | 禁用摘要 |

### code 命令

```bash
uv run ~/.claude/skills/searching-with-exa/scripts/exa_fetch.py code "query" [options]
```

专门用于代码搜索，默认：
- `category`: github
- `includeDomains`: github.com, stackoverflow.com, dev.to, medium.com
- `type`: deep
- 启用代码相关高亮提取

### contents 命令

```bash
uv run ~/.claude/skills/searching-with-exa/scripts/exa_fetch.py contents "url1" "url2" [options]
```

| CLI 参数 | API 参数 | 说明 |
|----------|----------|------|
| `urls` | `urls` | URL 列表 |
| `--livecrawl` | `livecrawl` | 抓取模式 |
| `--no-highlights` | - | 禁用高亮 |
| `--no-summary` | - | 禁用摘要 |

---

## 错误处理

### 常见错误码

| HTTP 状态码 | 说明 | 处理建议 |
|-------------|------|----------|
| 400 | 请求参数错误 | 检查参数格式 |
| 401 | API Key 无效 | 验证 API Key |
| 429 | 请求频率过高 | 降低请求频率 |
| 500 | 服务器错误 | 稍后重试 |

### 脚本错误输出

```
ERROR: API request failed: 401 Unauthorized
ERROR: Request timeout
ERROR: Please set your EXA API key in the script
```

---

## 成本说明

Exa API 按请求计费，成本因素：
- 搜索请求数
- 结果数量
- 内容抓取（text/highlights/summary）
- 实时抓取

响应中的 `costDollars` 字段显示实际成本。

---

## 最佳实践

### 性能优化

1. **减少不必要的内容抓取**
   ```bash
   # 仅需要 URL 时
   uv run ~/.claude/skills/searching-with-exa/scripts/exa_fetch.py search "query" --no-contents
   ```

2. **使用 category 缩小范围**
   ```bash
   # 比全网搜索更快更精准
   uv run ~/.claude/skills/searching-with-exa/scripts/exa_fetch.py search "React hooks" -c github
   ```

3. **限制结果数量**
   ```bash
   # 只需要 top 3
   uv run ~/.claude/skills/searching-with-exa/scripts/exa_fetch.py search "query" -n 3
   ```

### 质量优化

1. **使用 deep 模式获取全面结果**（默认）
2. **指定日期范围获取最新内容**
3. **使用 includeDomains 聚焦权威来源**

### 代码搜索

1. **优先使用 `code` 命令**
2. **指定具体编程语言或框架**
3. **包含 "example" 或 "tutorial" 关键词**

---

## 决策树

```
用户请求信息/文档/示例
    ↓
是否需要搜索多个来源？
    ├─ 否 → 已知具体 URL → 使用 `contents` 命令
    └─ 是 → 继续
    ↓
是否主要搜索代码/实现？
    ├─ 是 → 使用 `code` 命令
    └─ 否 → 使用 `search` 命令
    ↓
是否需要特定类别？
    ├─ GitHub 仓库 → 加 `-c github`
    ├─ 学术论文 → 加 `-c "research paper"`
    ├─ 新闻资讯 → 加 `-c news`
    └─ 通用搜索 → 不加 category
    ↓
执行命令并返回结果
```

---

## 类别说明

| 类别 | 说明 | 适用场景 |
|------|------|----------|
| `github` | GitHub 仓库 | 开源项目、代码参考 |
| `research paper` | 学术论文 | 技术研究、算法论文 |
| `news` | 新闻资讯 | 最新动态、发布公告 |
| `company` | 公司信息 | 企业介绍、产品信息 |
| `pdf` | PDF 文档 | 技术文档、白皮书 |
| `tweet` | Twitter | 社区讨论、快讯 |

---

## 最佳实践

1. **优先使用 `code` 命令** 搜索代码相关内容
2. **指定 category** 可显著提高结果相关性
3. **使用 `--start-date`** 获取最新内容
4. **限定域名** 聚焦官方文档或特定来源
5. **`--no-contents`** 快速浏览时使用，需详情再抓取

---

## 故障排查

### "API request failed"
- 检查 API Key 是否正确配置
- 确认网络连接正常

### 结果不相关
- 尝试更具体的查询词
- 使用 category 过滤
- 添加 include-domains 限制

### 抓取内容为空
- 尝试 `--livecrawl preferred` 启用实时抓取
- 部分网站可能阻止爬虫

---

## 注意事项

- 默认使用 `deep` 搜索模式，更全面但稍慢
- 搜索自动包含内容抓取、高亮和摘要
- 输出格式针对 Claude Code 优化
