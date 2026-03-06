def fetch_from_arxiv(query: str, limit: int = 5) -> List[Dict]:
    """
    备份引擎：从 arXiv 搜索（几乎无频率限制）
    """
    query = (query or "").strip()
    if not query:
        return []

    base_url = "http://export.arxiv.org/api/query?"
    search_query = f"all:{query}"
    params = f"search_query={search_query}&start=0&max_results={limit}"

    try:
        feed = feedparser.parse(base_url + params)
        papers: List[Dict] = []
        for entry in getattr(feed, "entries", []):
            title = getattr(entry, "title", "").replace("\n", " ").strip()
            abstract = getattr(entry, "summary", "").replace("\n", " ").strip()
            url = getattr(entry, "link", "").strip()
            published = getattr(entry, "published", "")
            year = published[:4] if published else "N/A"
            if not (title and abstract):
                continue
            papers.append({
                "title": title,
                "abstract": abstract,
                "url": url,
                "year": year,
                "source": "arXiv",
            })
        return papers
    except Exception as e:
        print(f"❌ arXiv 引擎也故障了: {e}")
        return []
      def fetch_papers(query: str, limit: int = 5) -> List[Dict]:
    """
    主引擎：带自动重试和故障切换的搜索。
    - 优先从 Semantic Scholar（可选用官方 API Key，支持更高频率）。
    - 如果触发 429 或返回为空，则自动切换到 arXiv。
    """
    query = (query or "").strip()
    if not query:
        return []

    api_key = os.getenv("SEMANTIC_SCHOLAR_API_KEY")
    headers = {"x-api-key": api_key} if api_key else {}

    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = {"query": query, "limit": limit, "fields": "title,abstract,url,year"}

    try:
        proxies = _get_scholar_proxies()
        response = _request_with_retry(url, params=params, headers=headers, proxies=proxies)

        if response.status_code == 429:
            return fetch_from_arxiv(query, limit)

        response.raise_for_status()
        data = response.json() or {}
        results = data.get("data", []) or []

        if not results:
            return fetch_from_arxiv(query, limit)

        for p in results:
            p["source"] = "Semantic Scholar"
        return results
    except Exception as e:
        print(f"⚠️ 主引擎连接异常: {e}，尝试备用引擎...")
        return fetch_from_arxiv(query, limit)
