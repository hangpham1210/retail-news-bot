from datetime import datetime


def parse_news(item: dict) -> dict:
    """
    Chuẩn hóa dữ liệu RSS
    """

    return {

        "source": item.get("source", ""),

        "title": item.get("title", "").strip(),

        # Dùng toàn văn do crawler lấy được; chỉ dùng RSS summary khi không có.
        "content": item.get("content") or item.get("summary", "").strip(),

        # topic mặc định
        "topic": item.get("category", ""),

        "summary": "",

        "published": normalize_date(
            item.get("published")
        ),

        "category": "",

        "importance": 0,

        "reason": "",

        "tags": [],

        "link": item.get("link", "")
    }



def normalize_date(date_value):

    if not date_value:
        return None

    return str(date_value)
