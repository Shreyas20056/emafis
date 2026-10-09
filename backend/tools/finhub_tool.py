import os
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from typing import List, Dict, Any


def fetch_stock_news(ticker: str, days_back: int = 7) -> List[Dict[str, Any]]:
    """
    Fetches stock and market news using NewsAPI.org (from GNEWS_API_KEY env variable),
    with fallbacks to Google News RSS feed and Finnhub API.
    """
    symbol = ticker.strip().upper()
    articles: List[Dict[str, Any]] = []

    # 1. Try NewsAPI.org using GNEWS_API_KEY
    gnews_key = os.getenv("GNEWS_API_KEY")
    if gnews_key:
        try:
            # Query format for Indian & Global stocks
            query = f'"{symbol}" OR "{symbol} stock" OR "{symbol} share"'
            url = f"https://newsapi.org/v2/everything?q={requests.utils.quote(query)}&sortBy=publishedAt&pageSize=10&language=en&apiKey={gnews_key}"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                news_items = data.get("articles", [])
                for item in news_items[:10]:
                    title = item.get("title", "")
                    desc = item.get("description", "") or title
                    if title and "[Removed]" not in title:
                        articles.append({
                            "headline": title,
                            "summary": desc[:300],
                            "source": item.get("source", {}).get("name", "NewsAPI"),
                            "url": item.get("url", ""),
                            "published_at": item.get("publishedAt", "")
                        })
                if articles:
                    print(f"[OK] Fetched {len(articles)} articles for {symbol} via NewsAPI.org")
                    return articles
        except Exception as e:
            print(f"[WARN] NewsAPI error for {symbol}: {e}")

    # 2. Fallback to Google News RSS (Free, real-time, no key required)
    try:
        rss_query = f"{symbol} stock market india"
        rss_url = f"https://news.google.com/rss/search?q={requests.utils.quote(rss_query)}&hl=en-IN&gl=IN&ceid=IN:en"
        response = requests.get(rss_url, timeout=5)
        if response.status_code == 200:
            root = ET.fromstring(response.text)
            for item in root.findall("./channel/item")[:10]:
                title = item.findtext("title", "")
                pub_date = item.findtext("pubDate", "")
                link = item.findtext("link", "")
                source_elem = item.find("source")
                source_name = source_elem.text if source_elem is not None else "Google News"
                if title:
                    articles.append({
                        "headline": title,
                        "summary": f"Recent market updates for {symbol}: {title}",
                        "source": source_name,
                        "url": link,
                        "published_at": pub_date
                    })
            if articles:
                print(f"[OK] Fetched {len(articles)} articles for {symbol} via Google News RSS")
                return articles
    except Exception as e:
        print(f"[WARN] Google News RSS error for {symbol}: {e}")

    # 3. Fallback to Finnhub API
    finnhub_key = os.getenv("FINNHUB_API_KEY")
    if finnhub_key:
        try:
            today = datetime.today().strftime('%Y-%m-%d')
            start_date = (datetime.today() - timedelta(days=days_back)).strftime('%Y-%m-%d')
            url = f"https://finnhub.io/api/v1/company-news?symbol={symbol}&from={start_date}&to={today}&token={finnhub_key}"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                news_items = response.json()[:10]
                for item in news_items:
                    articles.append({
                        "headline": item.get("headline"),
                        "summary": item.get("summary"),
                        "source": item.get("source", "Finnhub"),
                        "url": item.get("url"),
                        "published_at": datetime.fromtimestamp(item.get("datetime", 0)).isoformat() if item.get("datetime") else ""
                    })
                if articles:
                    return articles
        except Exception as e:
            print(f"[WARN] Finnhub API error for {symbol}: {e}")

    return articles