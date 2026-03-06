import requests
import feedparser

def fetch_from_arxiv(query, limit=5):
    """从 arXiv 获取文献"""
    base_url = "http://export.arxiv.org/api/query?"
    params = f"search_query=all:{query}&start=0&max_results={limit}"
    try:
        feed = feedparser.parse(base_url + params)
        papers = []
        for entry in feed.entries:
            papers.append({
                "title": entry.title.replace('\n', ' '),
                "abstract": entry.summary.replace('\n', ' '),
                "url": entry.link,
                "year": entry.published[:4] if hasattr(entry, 'published') else "N/A",
                "source": "arXiv"
            })
        return papers
    except Exception:
        return []

def fetch_papers(query, limit=5):
    """核心搜索函数：优先使用 Semantic Scholar，失败则回退到 arXiv"""
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = {
        "query": query, 
        "limit": limit, 
        "fields": "title,abstract,url,year"
    }
    try:
        # 使用较短的超时时间，防止卡死
        response = requests.get(url, params=params, timeout=5)
        if response.status_code == 200:
            data = response.json()
            results = data.get("data", [])
            if results:
                for p in results:
                    p['source'] = "Semantic Scholar"
                return results
        # 如果 SS 失败或无结果，转战 arXiv
        return fetch_from_arxiv(query, limit)
    except Exception:
        return fetch_from_arxiv(query, limit)
