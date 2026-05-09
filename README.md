# 多因子学术搜索引擎（课程展示版）

这是一个用于《网络搜索引擎》课程展示的 **白盒检索系统 Demo**。  
系统将三种打分信号融合排序，并在前端可视化展示每条结果的分数组成：

- **词法相关性**：BM25 倒排检索得分
- **语义相关性**：Sentence-Transformers 向量相似度
- **权威性**：模拟的权威分（课程演示用）

---

## 功能特性

- 基于 arXiv 论文数据构建本地检索库
- 支持多因子加权检索：`BM25 + 语义 + 权威`
- 支持实时调权重并重新排序
- 可视化展示每个结果的分数分解（白盒解释）
- 后端异步建索引，前端可轮询等待引擎就绪

---

## 项目结构

```text
Demo/
├─ data_collector.py      # 抓取 arXiv 数据并生成 data/papers.json
├─ engine.py              # 检索引擎（BM25 + 向量 + 融合排序）
├─ main.py                # FastAPI 服务入口
├─ requirements.txt       # Python 依赖
├─ data/
│  └─ papers.json         # 论文数据（由采集脚本生成）
└─ static/
   └─ index.html          # 前端页面（Vue + Tailwind）
```

---

## 环境要求

- Python 3.10+（建议）
- 可访问网络（首次运行会下载语义模型）

---

## 安装依赖

```bash
pip install -r requirements.txt
```

---

## 快速开始

### 1) 准备数据（首次）

```bash
python data_collector.py
```

执行后会在 `data/papers.json` 生成论文数据。

### 2) 启动服务

```bash
python main.py
```

启动后访问：  
`http://127.0.0.1:8000`

> 首次启动会加载并下载 `all-MiniLM-L6-v2` 语义模型，可能需要一些时间。  
> 在此期间前端会显示 loading 状态并自动重试。

---

## 检索接口

### `GET /api/search`

参数说明：

- `q`：查询词（必填）
- `w_bm25`：词法得分权重（默认 `1.0`）
- `w_sem`：语义得分权重（默认 `1.0`）
- `w_auth`：权威得分权重（默认 `1.0`）
- `top_k`：返回结果数（默认 `20`）

示例：

```text
/api/search?q=attention%20mechanism&w_bm25=2&w_sem=2&w_auth=0.5&top_k=20
```

返回结构（简化）：

```json
{
  "status": "ready",
  "results": [
    {
      "paper": { "...": "..." },
      "scores": {
        "bm25": 0.72,
        "semantic": 0.81,
        "authority": 0.33,
        "final": 2.39
      }
    }
  ]
}
```

当引擎尚未完成初始化时返回：

```json
{
  "status": "loading",
  "message": "Engine is building indices...",
  "results": []
}
```

---

## 排序逻辑（简述）

1. 对查询做分词，计算 BM25 分数并归一化  
2. 对查询编码为向量，与语料向量做余弦相似度并归一化  
3. 读取论文权威分并归一化  
4. 按以下公式融合：

```text
Final = w_bm25 * bm25 + w_sem * semantic + w_auth * authority
```

---

## 注意事项

- 权威分当前为随机模拟值（`Beta(2,5)` 分布），用于演示多因子融合，不代表真实引用影响力。
- 若出现 `No data found. Please run data_collector.py first.`，请先执行数据采集脚本。
- `data/papers.json` 可替换为你自己的论文或文档数据集（字段需与当前代码结构兼容）。

---

## 可扩展方向

- 接入真实引用图并计算 PageRank/影响力分
- 增加时间衰减、作者画像、机构可信度等信号
- 替换/增量构建索引，实现大规模数据检索
- 引入离线评测（NDCG、MAP、Recall@K）做权重调优

