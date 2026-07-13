from config.news_sources import NEWS_SOURCES
from config.settings import MAX_NEWS_PER_FEED

import feedparser
import trafilatura

from bs4 import BeautifulSoup


def clean_html(text):
    """
    Loại bỏ HTML trong RSS summary.
    """

    if not text:
        return ""

    return BeautifulSoup(
        text,
        "html.parser"
    ).get_text(" ", strip=True)


def get_article_content(url):
    """
    Lấy nội dung đầy đủ của bài báo.
    """

    try:

        downloaded = trafilatura.fetch_url(url)

        if not downloaded:
            return ""

        content = trafilatura.extract(downloaded)

        return content or ""

    except Exception as e:

        print(f"❌ Không lấy được nội dung: {url}")
        print(e)

        return ""


def crawl_source(source):

    feed = feedparser.parse(source["url"])

    results = []

    # Không tải toàn bộ RSS (có thể hàng chục bài) trong một lần chạy.
    for entry in feed.entries[:MAX_NEWS_PER_FEED]:

        link = entry.get("link", "")

        summary = clean_html(
            entry.get("summary", "")
        )

        # Ưu tiên lấy full article
        content = get_article_content(link)

        # Nếu không lấy được thì dùng RSS summary
        if not content:
            content = summary

        print(
            f"{source['name']} | "
            f"{len(content)} ký tự | "
            f"{entry.get('title', '')[:60]}"
        )

        results.append({

            "source": source["name"],

            "title": entry.get("title", ""),

            "summary": summary,

            "content": content,

            "published": entry.get("published"),

            "link": link

        })

    return results


def crawl_all():

    all_news = []

    for source in NEWS_SOURCES:

        print(f"\n===== {source['name']} =====")

        news = crawl_source(source)

        all_news.extend(news)

    return all_news


if __name__ == "__main__":

    data = crawl_all()

    print(f"\n📰 Total news: {len(data)}")

    if data:

        print("\n==============================")
        print("Tiêu đề:")
        print(data[0]["title"])

        print("\nĐộ dài content:")
        print(len(data[0]["content"]))

        print("\nNội dung (500 ký tự đầu):")
        print(data[0]["content"][:500])
