import asyncio
from bot.sender import send_news


news = [
    {
        "title": "Test Retail News Bot",
        "topic": "Testing",
        "importance": 10,
        "summary": [
            "Đây là tin kiểm tra bot.",
            "Telegram đang hoạt động.",
            "Launchd chạy thành công."
        ],
        "tags": [
            "test",
            "telegram"
        ],
        "link": "https://example.com"
    }
]


async def main():
    await send_news(news)


if __name__ == "__main__":
    asyncio.run(main())