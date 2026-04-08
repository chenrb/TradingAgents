# yfinance 使用分析 & 替换指南

## 1. yfinance 使用总览

yfinance 在项目中被用于 5 大数据类别，通过 `tradingagents/dataflows/interface.py` 统一路由。

### 涉及文件

| 文件 | 职责 |
|------|------|
| `tradingagents/dataflows/stockstats_utils.py` | OHLCV 数据获取、缓存、stockstats 指标计算基础 |
| `tradingagents/dataflows/y_finance.py` | 股价、技术指标、基本面、财报、内幕交易 |
| `tradingagents/dataflows/yfinance_news.py` | 个股新闻 & 全球宏观新闻 |
| `tradingagents/dataflows/interface.py` | 统一路由层，支持 yfinance / alpha_vantage 切换 |

---

## 2. 数据类别 & 具体 yfinance API 调用

### 2.1 OHLCV 股价数据 (`core_stock_apis`)

**工具**: `get_stock_data`
**路由函数**: `get_YFin_data_online()`
**文件**: `y_finance.py:9-48`

```python
yf.Ticker(symbol).history(start=start_date, end=end_date)
```

**返回字段**: Date, Open, High, Low, Close, Adj Close, Volume

---

### 2.2 OHLCV 批量数据（技术指标底层）

**函数**: `load_ohlcv()` (`stockstats_utils.py:47-88`)
**用于**: 所有技术指标计算的底层数据源

```python
yf.download(symbol, start=start_str, end=end_str, multi_level_index=False, progress=False, auto_adjust=True)
```

**缓存策略**: 5年数据，存为 CSV (`{symbol}-YFin-data-{start}-{end}.csv`)

---

### 2.3 技术指标 (`technical_indicators`)

**工具**: `get_indicators`
**路由函数**: `get_stock_stats_indicators_window()`
**文件**: `y_finance.py:50-185`

不直接调用 yfinance API 计算指标，而是基于 `load_ohlcv()` 获取的 OHLCV 数据，通过 **stockstats** 库本地计算。

**支持的指标**:

| 指标键 | 指标名称 | 类型 |
|--------|----------|------|
| `close_50_sma` | 50日简单移动平均线 | 移动平均 |
| `close_200_sma` | 200日简单移动平均线 | 移动平均 |
| `close_10_ema` | 10日指数移动平均线 | 移动平均 |
| `macd` | MACD 线 | MACD |
| `macds` | MACD 信号线 | MACD |
| `macdh` | MACD 柱状图 | MACD |
| `rsi` | 相对强弱指标 | 动量 |
| `boll` | 布林带中轨 | 波动率 |
| `boll_ub` | 布林带上轨 | 波动率 |
| `boll_lb` | 布林带下轨 | 波动率 |
| `atr` | 真实波动幅度均值 | 波动率 |
| `vwma` | 成交量加权移动平均 | 成交量 |
| `mfi` | 资金流量指标 | 成交量 |

> **注意**: 这些指标的计算依赖 stockstats，而非 yfinance 自身。替换 yfinance 只需确保替代品能提供同等质量的 OHLCV 数据。

---

### 2.4 公司基本面 (`fundamental_data - get_fundamentals`)

**路由函数**: `get_fundamentals()`
**文件**: `y_finance.py:248-302`

```python
yf.Ticker(ticker).info  # 字典对象
```

**提取的字段**:

| 字段 | yfinance info 键 | 说明 |
|------|------------------|------|
| 公司全名 | `longName` | |
| 行业 | `sector` | |
| 产业 | `industry` | |
| 市值 | `marketCap` | |
| 市盈率(TTM) | `trailingPE` | |
| 远期市盈率 | `forwardPE` | |
| PEG 比率 | `pegRatio` | |
| 市净率 | `priceToBook` | |
| 每股收益(TTM) | `trailingEps` | |
| 远期每股收益 | `forwardEps` | |
| 股息率 | `dividendYield` | |
| Beta | `beta` | |
| 52周最高 | `fiftyTwoWeekHigh` | |
| 52周最低 | `fiftyTwoWeekLow` | |
| 50日均线 | `fiftyDayAverage` | |
| 200日均线 | `twoHundredDayAverage` | |
| 营收(TTM) | `totalRevenue` | |
| 毛利润 | `grossProfits` | |
| EBITDA | `ebitda` | |
| 净利润 | `netIncomeToCommon` | |
| 净利率 | `profitMargins` | |
| 营业利润率 | `operatingMargins` | |
| 净资产收益率 | `returnOnEquity` | |
| 总资产收益率 | `returnOnAssets` | |
| 负债权益比 | `debtToEquity` | |
| 流动比率 | `currentRatio` | |
| 每股净资产 | `bookValue` | |
| 自由现金流 | `freeCashflow` | |

---

### 2.5 资产负债表 (`fundamental_data - get_balance_sheet`)

**路由函数**: `get_balance_sheet()`
**文件**: `y_finance.py:305-334`

```python
yf.Ticker(ticker).quarterly_balance_sheet  # 季度
yf.Ticker(ticker).balance_sheet            # 年度
```

**返回**: DataFrame，行=科目（Total Assets, Total Liabilities 等），列=财报期间

---

### 2.6 现金流量表 (`fundamental_data - get_cashflow`)

**路由函数**: `get_cashflow()`
**文件**: `y_finance.py:337-366`

```python
yf.Ticker(ticker).quarterly_cashflow  # 季度
yf.Ticker(ticker).cashflow            # 年度
```

**返回**: DataFrame，行=科目（Operating Cash Flow 等），列=财报期间

---

### 2.7 利润表 (`fundamental_data - get_income_statement`)

**路由函数**: `get_income_statement()`
**文件**: `y_finance.py:369-398`

```python
yf.Ticker(ticker).quarterly_income_stmt  # 季度
yf.Ticker(ticker).income_stmt            # 年度
```

**返回**: DataFrame，行=科目（Total Revenue, Net Income 等），列=财报期间

---

### 2.8 内幕交易 (`news_data - get_insider_transactions`)

**路由函数**: `get_insider_transactions()`
**文件**: `y_finance.py:401-421`

```python
yf.Ticker(ticker).insider_transactions
```

**返回**: DataFrame，包含内幕人士买卖记录

---

### 2.9 个股新闻 (`news_data - get_news`)

**路由函数**: `get_news_yfinance()`
**文件**: `yfinance_news.py:51-104`

```python
yf.Ticker(ticker).get_news(count=20)
```

**返回**: 文章列表，提取 title, summary, publisher, link, pub_date

---

### 2.10 全球宏观新闻 (`news_data - get_global_news`)

**路由函数**: `get_global_news_yfinance()`
**文件**: `yfinance_news.py:107-197`

```python
yf.Search(query=q, news_count=limit, enable_fuzzy_query=True)
```

**搜索关键词**: "stock market economy", "Federal Reserve interest rates", "inflation economic outlook", "global markets trading"

---

## 3. 公共基础设施

### 3.1 重试机制 `yf_retry()`

**文件**: `stockstats_utils.py:15-31`

对 `YFRateLimitError` 进行指数退避重试（最多3次，基础延迟2秒）。

### 3.2 财报日期过滤 `filter_financials_by_date()`

**文件**: `stockstats_utils.py:91-102`

过滤掉 curr_date 之后的财报列，防止回测时前视偏差。

---

## 4. yfinance API 汇总

| yfinance API | 用途 | 调用位置 |
|--------------|------|----------|
| `yf.Ticker(s).history(start, end)` | OHLCV 股价 | `y_finance.py:22` |
| `yf.download(symbol, start, end)` | 批量 OHLCV（带缓存） | `stockstats_utils.py:72` |
| `yf.Ticker(s).info` | 公司基本面快照 | `y_finance.py:255` |
| `yf.Ticker(s).quarterly_balance_sheet` | 季度资产负债表 | `y_finance.py:315` |
| `yf.Ticker(s).balance_sheet` | 年度资产负债表 | `y_finance.py:317` |
| `yf.Ticker(s).quarterly_cashflow` | 季度现金流量表 | `y_finance.py:347` |
| `yf.Ticker(s).cashflow` | 年度现金流量表 | `y_finance.py:349` |
| `yf.Ticker(s).quarterly_income_stmt` | 季度利润表 | `y_finance.py:379` |
| `yf.Ticker(s).income_stmt` | 年度利润表 | `y_finance.py:381` |
| `yf.Ticker(s).insider_transactions` | 内幕交易 | `y_finance.py:407` |
| `yf.Ticker(s).get_news(count)` | 个股新闻 | `yfinance_news.py:69` |
| `yf.Search(query, news_count)` | 全球新闻搜索 | `yfinance_news.py:136` |
| `yfinance.exceptions.YFRateLimitError` | 限流异常 | `stockstats_utils.py:6` |

---

## 5. 替换需满足的数据需求

替代品需提供以下能力：

### 必须具备
1. **OHLCV 股价数据** — 至少5年历史，支持日期范围查询
2. **公司基本面快照** — 市值、PE、EPS、利润率、ROE 等 27+ 字段
3. **三大财务报表** — 资产负债表、利润表、现金流量表（支持季度/年度）
4. **内幕交易数据**
5. **个股新闻** — 按日期范围过滤
6. **全球/宏观新闻搜索**

### 加分项
7. **速率限制处理** — yfinance 经常被限流
8. **数据稳定性** — yfinance 的 `info` 字段名可能随版本变化
9. **无需 API Key** — yfinance 的优势之一

### 替换架构建议

项目已有 `interface.py` 路由层，替换策略：
1. 在 `dataflows/` 下新建模块（如 `new_vendor.py`）
2. 在 `interface.py` 的 `VENDOR_METHODS` 中注册
3. 在 `default_config.py` 中切换 `data_vendors` 配置
4. 保持函数签名和返回格式（CSV 字符串）不变
