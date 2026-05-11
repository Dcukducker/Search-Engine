# 网络搜索引擎课程 Demo（多因子可解释检索）

这是一个用于课程展示的学术搜索 Demo，后端融合三种信号做排序，前端可视化每条结果的分数组成：

- BM25（词法匹配）
- 语义相似度（Sentence-Transformers）
- 权威分（演示用模拟值）

---

## 你需要先知道的一点

本仓库已忽略 `data/` 目录（未上传数据文件），所以克隆后**不能直接搜索**。  
请先运行数据采集脚本生成 `data/papers.json`，再启动服务。

---

## 项目结构

```text
Demo/
├─ data_collector.py      # 抓取 arXiv 数据并生成 data/papers.json
├─ engine.py              # 检索引擎（BM25 + 语义向量 + 融合排序）
├─ main.py                # FastAPI 服务入口
├─ requirements.txt       # 依赖
└─ static/
   └─ index.html          # 前端页面（Vue + Tailwind）
```

---

## 环境要求

- Python 3.10+（建议）
- 能访问网络（首次会下载语义模型）

---

## 一分钟上手（复制即可）

```bash
# 1) 安装依赖
pip install -r requirements.txt

# 2) 生成数据（因为 data/ 未上传）
python data_collector.py

# 3) 启动服务
python main.py
```

打开浏览器访问：`http://127.0.0.1:8000`

> 首次启动会下载 `all-MiniLM-L6-v2`，界面可能短暂显示 loading。

---

## 使用方法（给第一次使用的人）

1. 打开页面后，在搜索框输入关键词（如 `attention mechanism`）。  
2. 点击 **Search** 查看结果。  
3. 调整三个滑块权重：
   - **Lexical Score**：更看重关键词字面匹配
   - **Semantic Vector**：更看重语义接近
   - **Authority**：更看重论文“权威度”（模拟）
4. 页面右侧会显示每条结果的分项得分和最终融合得分。

---

## API（可选）

### `GET /api/search`

参数：

- `q`：查询词（必填）
- `w_bm25`：BM25 权重（默认 `1.0`）
- `w_sem`：语义权重（默认 `1.0`）
- `w_auth`：权威权重（默认 `1.0`）
- `top_k`：返回条数（默认 `20`）

示例：

```text
/api/search?q=attention%20mechanism&w_bm25=2&w_sem=2&w_auth=0.5&top_k=20
```

---

## 常见问题

### 1) 提示 `No data found. Please run data_collector.py first.`

说明你还没生成数据，执行：

```bash
python data_collector.py
```

### 2) 为什么第一次启动很慢？

会下载语义模型并建立索引，属于正常现象，后续会快很多。

### 3) 权威分真实吗？

当前是课程演示用的模拟值（Beta 分布），不是实际引用网络计算结果。

---

## 排序公式

```text
Final = w_bm25 * bm25 + w_sem * semantic + w_auth * authority
```

