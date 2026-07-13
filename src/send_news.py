import asyncio

from pipeline import run_pipeline
from bot.sender import send_news

# ==========================
# Cấu hình
# ==========================
MIN_IMPORTANCE = 7
MAX_NEWS = 15


async def main():

    news = run_pipeline()

    print(f"Pipeline trả về: {len(news)} bài")

    # Lọc theo độ quan trọng
    news = [
        x for x in news
        if x.get("importance", 0) >= MIN_IMPORTANCE
    ]

    # Sắp xếp giảm dần theo importance
    news = sorted(
        news,
        key=lambda x: x.get("importance", 0),
        reverse=True
    )

    # Chỉ lấy N bài đầu
    news = news[:MAX_NEWS]

    print(f"Sẽ gửi: {len(news)} bài")

    await send_news(news)


if __name__ == "__main__":
    try:
        asyncio.run(main())
        print("✅ Pipeline completed")
    except Exception as e:
        print(f"❌ Pipeline failed: {e}")