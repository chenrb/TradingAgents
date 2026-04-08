"""
yfinance API 使用测试脚本

逐个测试项目中所有 yfinance 调用点，验证当前数据可用性。
用于评估替代方案时确认数据完整性。

用法:
    python tests/test_yfinance_apis.py AAPL
    python tests/test_yfinance_apis.py AAPL --date 2025-01-15
"""

import sys
import json
import time
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

import pandas as pd
import yfinance as yf
from yfinance.exceptions import YFRateLimitError


def yf_retry(func, max_retries=3, base_delay=2.0):
    for attempt in range(max_retries + 1):
        try:
            return func()
        except YFRateLimitError:
            if attempt < max_retries:
                delay = base_delay * (2 ** attempt)
                print(f"  [RETRY] Rate limited, waiting {delay:.0f}s (attempt {attempt + 1}/{max_retries})")
                time.sleep(delay)
            else:
                raise


def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def test_ohlcv_ticker_history(symbol, start_date, end_date):
    """Test: yf.Ticker(s).history(start, end) — y_finance.py:22"""
    print_section("1. OHLCV via Ticker.history()")

    try:
        ticker = yf.Ticker(symbol)
        data = yf_retry(lambda: ticker.history(start=start_date, end=end_date))

        if data.empty:
            print(f"  [FAIL] No data returned")
            return False

        print(f"  [OK] {len(data)} records")
        print(f"  Columns: {list(data.columns)}")
        print(f"  Date range: {data.index[0]} ~ {data.index[-1]}")
        print(f"  Sample (last 3 rows):")
        print(data.tail(3).to_string())
        return True
    except Exception as e:
        print(f"  [FAIL] {e}")
        return False


def test_ohlcv_download(symbol, curr_date):
    """Test: yf.download() — stockstats_utils.py:72 (load_ohlcv)"""
    print_section("2. OHLCV via yf.download() (bulk, 5yr)")

    today = pd.Timestamp.today()
    start = today - pd.DateOffset(years=5)

    try:
        data = yf_retry(lambda: yf.download(
            symbol,
            start=start.strftime("%Y-%m-%d"),
            end=today.strftime("%Y-%m-%d"),
            multi_level_index=False,
            progress=False,
            auto_adjust=True,
        ))

        if data.empty:
            print(f"  [FAIL] No data returned")
            return False

        data = data.reset_index()
        print(f"  [OK] {len(data)} records")
        print(f"  Columns: {list(data.columns)}")
        print(f"  Date range: {data['Date'].iloc[0]} ~ {data['Date'].iloc[-1]}")
        return True
    except Exception as e:
        print(f"  [FAIL] {e}")
        return False


def test_fundamentals(symbol):
    """Test: yf.Ticker(s).info — y_finance.py:255 (get_fundamentals)"""
    print_section("3. Company Fundamentals (Ticker.info)")

    fields = {
        "longName": "公司全名",
        "sector": "行业",
        "industry": "产业",
        "marketCap": "市值",
        "trailingPE": "市盈率(TTM)",
        "forwardPE": "远期市盈率",
        "pegRatio": "PEG比率",
        "priceToBook": "市净率",
        "trailingEps": "每股收益(TTM)",
        "forwardEps": "远期每股收益",
        "dividendYield": "股息率",
        "beta": "Beta",
        "fiftyTwoWeekHigh": "52周最高",
        "fiftyTwoWeekLow": "52周最低",
        "fiftyDayAverage": "50日均线",
        "twoHundredDayAverage": "200日均线",
        "totalRevenue": "营收(TTM)",
        "grossProfits": "毛利润",
        "ebitda": "EBITDA",
        "netIncomeToCommon": "净利润",
        "profitMargins": "净利率",
        "operatingMargins": "营业利润率",
        "returnOnEquity": "净资产收益率",
        "returnOnAssets": "总资产收益率",
        "debtToEquity": "负债权益比",
        "currentRatio": "流动比率",
        "bookValue": "每股净资产",
        "freeCashflow": "自由现金流",
    }

    try:
        ticker = yf.Ticker(symbol)
        info = yf_retry(lambda: ticker.info)

        if not info:
            print(f"  [FAIL] No info returned")
            return False

        available = 0
        missing = []
        for key, label in fields.items():
            value = info.get(key)
            if value is not None:
                available += 1
                print(f"  [OK] {label} ({key}): {value}")
            else:
                missing.append(key)
                print(f"  [--] {label} ({key}): N/A")

        print(f"\n  Summary: {available}/{len(fields)} fields available")
        if missing:
            print(f"  Missing: {missing}")
        return available > 0
    except Exception as e:
        print(f"  [FAIL] {e}")
        return False


def test_balance_sheet(symbol):
    """Test: Ticker.balance_sheet / quarterly_balance_sheet — y_finance.py:315-317"""
    print_section("4. Balance Sheet")

    try:
        ticker = yf.Ticker(symbol)

        for freq, attr in [("quarterly", "quarterly_balance_sheet"), ("annual", "balance_sheet")]:
            data = yf_retry(lambda a=attr: getattr(ticker, a))
            if data is not None and not data.empty:
                print(f"  [OK] {freq}: {data.shape[0]} rows x {data.shape[1]} periods")
                print(f"  Rows: {list(data.index[:5])}...")
                print(f"  Columns (dates): {[str(c) for c in data.columns[:3]]}...")
            else:
                print(f"  [FAIL] {freq}: No data")
        return True
    except Exception as e:
        print(f"  [FAIL] {e}")
        return False


def test_cashflow(symbol):
    """Test: Ticker.cashflow / quarterly_cashflow — y_finance.py:347-349"""
    print_section("5. Cash Flow Statement")

    try:
        ticker = yf.Ticker(symbol)

        for freq, attr in [("quarterly", "quarterly_cashflow"), ("annual", "cashflow")]:
            data = yf_retry(lambda a=attr: getattr(ticker, a))
            if data is not None and not data.empty:
                print(f"  [OK] {freq}: {data.shape[0]} rows x {data.shape[1]} periods")
                print(f"  Rows: {list(data.index[:5])}...")
            else:
                print(f"  [FAIL] {freq}: No data")
        return True
    except Exception as e:
        print(f"  [FAIL] {e}")
        return False


def test_income_statement(symbol):
    """Test: Ticker.income_stmt / quarterly_income_stmt — y_finance.py:379-381"""
    print_section("6. Income Statement")

    try:
        ticker = yf.Ticker(symbol)

        for freq, attr in [("quarterly", "quarterly_income_stmt"), ("annual", "income_stmt")]:
            data = yf_retry(lambda a=attr: getattr(ticker, a))
            if data is not None and not data.empty:
                print(f"  [OK] {freq}: {data.shape[0]} rows x {data.shape[1]} periods")
                print(f"  Rows: {list(data.index[:5])}...")
            else:
                print(f"  [FAIL] {freq}: No data")
        return True
    except Exception as e:
        print(f"  [FAIL] {e}")
        return False


def test_insider_transactions(symbol):
    """Test: Ticker.insider_transactions — y_finance.py:407"""
    print_section("7. Insider Transactions")

    try:
        ticker = yf.Ticker(symbol)
        data = yf_retry(lambda: ticker.insider_transactions)

        if data is not None and not data.empty:
            print(f"  [OK] {len(data)} records")
            print(f"  Columns: {list(data.columns)}")
            print(data.head(3).to_string())
        else:
            print(f"  [WARN] No insider transactions data (may be normal for some stocks)")
        return True
    except Exception as e:
        print(f"  [FAIL] {e}")
        return False


def test_stock_news(symbol, start_date, end_date):
    """Test: Ticker.get_news() — yfinance_news.py:69"""
    print_section("8. Stock News (Ticker.get_news)")

    try:
        ticker = yf.Ticker(symbol)
        news = yf_retry(lambda: ticker.get_news(count=20))

        if not news:
            print(f"  [FAIL] No news returned")
            return False

        print(f"  [OK] {len(news)} articles")

        for i, article in enumerate(news[:3]):
            if "content" in article:
                content = article["content"]
                title = content.get("title", "No title")
                publisher = content.get("provider", {}).get("displayName", "Unknown")
            else:
                title = article.get("title", "No title")
                publisher = article.get("publisher", "Unknown")

            print(f"  [{i+1}] {title} ({publisher})")

        return True
    except Exception as e:
        print(f"  [FAIL] {e}")
        return False


def test_global_news(curr_date):
    """Test: yf.Search() — yfinance_news.py:136"""
    print_section("9. Global News (yf.Search)")

    queries = [
        "stock market economy",
        "Federal Reserve interest rates",
    ]

    try:
        for query in queries:
            search = yf_retry(lambda q=query: yf.Search(
                query=q,
                news_count=5,
                enable_fuzzy_query=True,
            ))

            if search.news:
                print(f"  [OK] Query='{query}': {len(search.news)} articles")
                for article in search.news[:2]:
                    if "content" in article:
                        title = article["content"].get("title", "No title")
                    else:
                        title = article.get("title", "No title")
                    print(f"    - {title}")
            else:
                print(f"  [FAIL] Query='{query}': No results")

        return True
    except Exception as e:
        print(f"  [FAIL] {e}")
        return False


def test_technical_indicators(symbol, curr_date):
    """Test: stockstats indicators on yfinance OHLCV data — y_finance.py:50-185"""
    print_section("10. Technical Indicators (via stockstats on yfinance OHLCV)")

    from stockstats import wrap

    indicators = [
        "close_50_sma", "close_200_sma", "close_10_ema",
        "macd", "macds", "macdh",
        "rsi",
        "boll", "boll_ub", "boll_lb",
        "atr",
        "vwma", "mfi",
    ]

    today = pd.Timestamp.today()
    start = today - pd.DateOffset(years=5)

    try:
        data = yf_retry(lambda: yf.download(
            symbol,
            start=start.strftime("%Y-%m-%d"),
            end=today.strftime("%Y-%m-%d"),
            multi_level_index=False,
            progress=False,
            auto_adjust=True,
        ))
        data = data.reset_index()
        data["Date"] = pd.to_datetime(data["Date"], errors="coerce")
        data = data.dropna(subset=["Date"])
        price_cols = [c for c in ["Open", "High", "Low", "Close", "Volume"] if c in data.columns]
        data[price_cols] = data[price_cols].apply(pd.to_numeric, errors="coerce")
        data = data.dropna(subset=["Close"])

        df = wrap(data)
        df["Date"] = df["Date"].dt.strftime("%Y-%m-%d")
        curr_date_str = pd.to_datetime(curr_date).strftime("%Y-%m-%d")

        for ind in indicators:
            try:
                df[ind]  # trigger calculation
                matching = df[df["Date"].str.startswith(curr_date_str)]
                if not matching.empty:
                    val = matching[ind].values[0]
                    print(f"  [OK] {ind}: {val}")
                else:
                    print(f"  [--] {ind}: N/A (not a trading day)")
            except Exception as e:
                print(f"  [FAIL] {ind}: {e}")

        return True
    except Exception as e:
        print(f"  [FAIL] {e}")
        return False


def main():
    symbol = sys.argv[1] if len(sys.argv) > 1 else "AAPL"
    curr_date = "2025-03-01"
    start_date = "2025-02-01"
    end_date = "2025-03-01"

    # Parse --date arg
    for i, arg in enumerate(sys.argv):
        if arg == "--date" and i + 1 < len(sys.argv):
            curr_date = sys.argv[i + 1]
            dt = datetime.strptime(curr_date, "%Y-%m-%d")
            start_date = (dt - relativedelta(days=30)).strftime("%Y-%m-%d")
            end_date = curr_date

    print(f"Testing yfinance APIs for symbol={symbol}")
    print(f"Date range: {start_date} ~ {end_date}, curr_date={curr_date}")

    results = {}

    results["ohlcv_history"] = test_ohlcv_ticker_history(symbol, start_date, end_date)
    results["ohlcv_download"] = test_ohlcv_download(symbol, curr_date)
    results["fundamentals"] = test_fundamentals(symbol)
    results["balance_sheet"] = test_balance_sheet(symbol)
    results["cashflow"] = test_cashflow(symbol)
    results["income_statement"] = test_income_statement(symbol)
    results["insider_transactions"] = test_insider_transactions(symbol)
    results["stock_news"] = test_stock_news(symbol, start_date, end_date)
    results["global_news"] = test_global_news(curr_date)
    results["technical_indicators"] = test_technical_indicators(symbol, curr_date)

    print_section("SUMMARY")
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    for name, ok in results.items():
        status = "PASS" if ok else "FAIL"
        print(f"  [{status}] {name}")
    print(f"\n  Total: {passed}/{total} passed")

    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
