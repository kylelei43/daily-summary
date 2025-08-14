import os
from typing import Iterable, List, Dict, Optional

import requests


def fetch_top_headlines(
    keywords: Optional[Iterable[str]] = None,
    category: Optional[str] = None,
    limit: int = 5,
) -> List[Dict[str, str]]:
    """Fetch top headlines from NewsAPI.

    Args:
        keywords: An iterable of keywords used to search articles. If provided
            it takes precedence over ``category``. A single string is also
            accepted.
        category: News category such as ``business`` or ``technology``.
        limit: Maximum number of stories to return. The value is clamped between
            3 and 5.

    Returns:
        A list of dictionaries each containing ``title`` and ``url``.

    Raises:
        EnvironmentError: If the ``NEWS_API_KEY`` environment variable is not
            set.
        ValueError: If neither ``keywords`` nor ``category`` are provided.
        requests.HTTPError: If the request to NewsAPI fails.
    """

    api_key = os.getenv("NEWS_API_KEY")
    if not api_key:
        raise EnvironmentError("NEWS_API_KEY is not set in environment variables")

    if not keywords and not category:
        raise ValueError("Either keywords or category must be provided")

    if isinstance(keywords, str):
        keywords = [keywords]

    # Clamp limit between 3 and 5
    limit = max(3, min(5, limit))

    params = {"apiKey": api_key, "pageSize": limit}
    if keywords:
        params["q"] = " ".join(keywords)
    elif category:
        params["category"] = category

    response = requests.get("https://newsapi.org/v2/top-headlines", params=params, timeout=10)
    response.raise_for_status()
    data = response.json()
    articles = data.get("articles", [])

    results = []
    for article in articles[:limit]:
        title = article.get("title")
        url = article.get("url")
        if title and url:
            results.append({"title": title, "url": url})

    return results
