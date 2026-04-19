# TradingAgents A股数据需求清单

TradingAgents 多智能体交易框架从数据库读取数据，替代 yfinance。
以下为全部所需数据表和字段定义。

---

## 已有数据（无需同步）

### daily_quotes（日行情）

| 字段 | 类型 | 说明 |
|------|------|------|
| code | varchar(10) | 股票代码，如 sh.600000 |
| trade_date | date | 交易日期 |
| open | decimal(10,3) | 开盘价 |
| high | decimal(10,3) | 最高价 |
| low | decimal(10,3) | 最低价 |
| close | decimal(10,3) | 收盘价 |
| volume | bigint | 成交量 |
| amount | decimal(18,3) | 成交额 |
| pct_chg | decimal(8,3) | 涨跌幅% |
| turn | decimal(8,4) | 换手率% |
| pe_ttm | decimal(12,3) | 滚动市盈率 |
| pb_mrq | decimal(12,3) | 市净率 |

### stock_list（股票列表）

| 字段 | 类型 | 说明 |
|------|------|------|
| code | varchar(10) | 股票代码 |
| name | varchar(20) | 股票名称 |

### stock_sector + sector_list（行业板块）

| 字段 | 类型 | 说明 |
|------|------|------|
| code | varchar(10) | 股票代码 |
| sector_code | varchar(20) | 板块代码 |
| sector_name | varchar(30) | 板块名称 |

---

## 需要同步的数据

### 1. share_structure（股本结构）

**优先级: P1** | 用途: 计算市值（close × total_share）

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| code | varchar(10) | 是 | 股票代码 |
| trade_date | date | 是 | 变更日期 |
| total_share | bigint | 是 | 总股本 |
| float_share | bigint | 否 | 流通股本 |

**说明:** 股本结构不常变化，建议按公告日同步变更记录即可。

---

### 2. income_statement（利润表）

**优先级: P1** | 用途: 基本面分析师分析盈利能力

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| code | varchar(10) | 是 | 股票代码 |
| report_date | date | 是 | 报告期截止日 |
| report_type | varchar(10) | 是 | 报告类型: Q1 / Q2 / Q3 / annual |
| total_revenue | decimal(18,3) | 是 | 营业总收入 |
| revenue | decimal(18,3) | 是 | 营业收入 |
| total_cogs | decimal(18,3) | 否 | 营业总成本 |
| cogs | decimal(18,3) | 否 | 营业成本 |
| gross_profit | decimal(18,3) | 是 | 毛利润 |
| operating_profit | decimal(18,3) | 否 | 营业利润 |
| total_profit | decimal(18,3) | 否 | 利润总额 |
| net_income | decimal(18,3) | 否 | 净利润 |
| net_income_parent | decimal(18,3) | 是 | 归母净利润 |
| eps | decimal(10,4) | 否 | 基本每股收益 |
| diluted_eps | decimal(10,4) | 否 | 稀释每股收益 |

**说明:** 需要季报和年报。report_date 为报告期截止日（如 2025-12-31），非发布日期。

---

### 3. balance_sheet（资产负债表）

**优先级: P1** | 用途: 基本面分析师分析财务健康度

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| code | varchar(10) | 是 | 股票代码 |
| report_date | date | 是 | 报告期截止日 |
| report_type | varchar(10) | 是 | 报告类型: Q1 / Q2 / Q3 / annual |
| total_assets | decimal(18,3) | 是 | 总资产 |
| total_current_assets | decimal(18,3) | 否 | 流动资产合计 |
| total_non_current_assets | decimal(18,3) | 否 | 非流动资产合计 |
| total_liabilities | decimal(18,3) | 是 | 总负债 |
| total_current_liabilities | decimal(18,3) | 否 | 流动负债合计 |
| total_non_current_liabilities | decimal(18,3) | 否 | 非流动负债合计 |
| total_equity | decimal(18,3) | 是 | 所有者权益合计 |
| equity_parent | decimal(18,3) | 是 | 归母所有者权益 |
| cash | decimal(18,3) | 否 | 货币资金 |
| accounts_receivable | decimal(18,3) | 否 | 应收账款 |
| inventory | decimal(18,3) | 否 | 存货 |
| short_term_debt | decimal(18,3) | 否 | 短期借款 |
| long_term_debt | decimal(18,3) | 否 | 长期借款 |

**说明:** 需要季报和年报。

---

### 4. cashflow_statement（现金流量表）

**优先级: P1** | 用途: 基本面分析师分析现金流健康度

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| code | varchar(10) | 是 | 股票代码 |
| report_date | date | 是 | 报告期截止日 |
| report_type | varchar(10) | 是 | 报告类型: Q1 / Q2 / Q3 / annual |
| ocf | decimal(18,3) | 是 | 经营活动现金流净额 |
| icf | decimal(18,3) | 否 | 投资活动现金流净额 |
| fcf | decimal(18,3) | 否 | 筹资活动现金流净额 |
| net_change_cash | decimal(18,3) | 否 | 现金净增加额 |
| capex | decimal(18,3) | 否 | 资本性支出 |

**说明:** 需要季报和年报。ocf（经营现金流）是最关键的指标。

---

### 5. dividend（分红/股息）

**优先级: P2** | 用途: 计算股息率

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| code | varchar(10) | 是 | 股票代码 |
| ex_date | date | 是 | 除权除息日 |
| div_type | varchar(20) | 是 | 类型: cash(现金) / stock(送股) / convert(转增) |
| div_amount | decimal(10,4) | 是 | 每股分红金额（现金分红） |

---

### 6. stock_news（个股新闻）

**优先级: P2** | 用途: 新闻分析师、社媒分析师

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| title | varchar(200) | 是 | 新闻标题 |
| content | text | 否 | 新闻正文或摘要 |
| source | varchar(50) | 否 | 来源（如: 东方财富、财联社） |
| url | varchar(500) | 否 | 原文链接 |
| pub_date | datetime | 是 | 发布时间 |
| related_codes | varchar(200) | 是 | 关联股票代码，多个用逗号分隔 |

**说明:** 每只股票每次分析取最近 20 条，建议保留近 30 天数据。

---

### 7. macro_news（宏观/市场新闻）

**优先级: P2** | 用途: 新闻分析师（全球宏观视角）

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| title | varchar(200) | 是 | 新闻标题 |
| content | text | 否 | 新闻正文或摘要 |
| source | varchar(50) | 否 | 来源 |
| url | varchar(500) | 否 | 原文链接 |
| pub_date | datetime | 是 | 发布时间 |
| category | varchar(30) | 否 | 分类: monetary_policy / economic_data / market_dynamic / industry_policy |

**说明:** 每次分析取最近 10 条，建议保留近 7 天数据。关键词覆盖: 货币政策、经济数据、市场动态、行业政策。

---

## 不需要同步（可从已有数据计算）

以下指标由 TradingAgents 从数据库数据本地计算，无需额外存储:

| 指标 | 计算方式 |
|------|---------|
| 总市值 | close × total_share |
| EPS | close / pe_ttm |
| 毛利率 | gross_profit / revenue |
| 净利率 | net_income / total_revenue |
| 营业利润率 | operating_profit / total_revenue |
| ROE | net_income_parent / equity_parent |
| ROA | net_income / total_assets |
| 资产负债率 | total_liabilities / total_assets |
| 流动比率 | total_current_assets / total_current_liabilities |
| 52周最高/最低 | daily_quotes 按近250个交易日聚合 |
| 50日/200日均价 | ma_daily.ma50 / ma_daily.ma250 |
| 技术指标(MACD/布林/ATR等) | 从 daily_quotes OHLCV 数据本地计算 |

---

## 同步优先级总结

| 顺序 | 表名 | 优先级 | 说明 |
|------|------|--------|------|
| 1 | share_structure | P1 | 股本结构，计算市值用 |
| 2 | income_statement | P1 | 利润表，基本面分析核心 |
| 3 | balance_sheet | P1 | 资产负债表，基本面分析核心 |
| 4 | cashflow_statement | P1 | 现金流量表，基本面分析核心 |
| 5 | dividend | P2 | 分红数据，股息率计算 |
| 6 | stock_news | P2 | 个股新闻，新闻分析师用 |
| 7 | macro_news | P2 | 宏观新闻，新闻分析师用 |

P1 为必须数据，缺少则基本面分析师无法工作。
P2 为增强数据，缺少可暂时用第三方 API 实时获取。
