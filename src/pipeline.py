import sys
import os


# Cho phép import các folder ở root project
PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

sys.path.append(PROJECT_ROOT)



from news.crawler import crawl_all
from news.parser import parse_news
from config.settings import MAX_NEWS_PER_RUN


from src.database.history import (
    init_db,
    is_exist,
    save_news,
    get_unsent_news,
)


from ai.summarizer import fallback_summary, is_quota_error, summarize_article




def run_pipeline():

    print("🚀 Start pipeline")


    # Khởi tạo database
    init_db()



    # =========================
    # 1. Crawl RSS
    # =========================

    raw_news = crawl_all()


    print(
        f"📰 Total crawled: {len(raw_news)}"
    )



    new_news = []
    gemini_unavailable = False



    # =========================
    # 2. Process từng bài
    # =========================

    for item in raw_news[:MAX_NEWS_PER_RUN]:


        # Parse format chuẩn

        news = parse_news(item)



        link = news.get("link")


        if not link:
            continue



        # =========================
        # 3. Check duplicate
        # =========================

        if is_exist(link):

            print(
                "⏭ Skip:",
                news["title"]
            )

            continue



        print(
            "\n📝 Processing:",
            news["title"]
        )



        # =========================
        # 4. Gemini summarize
        # =========================

        if gemini_unavailable:
            news.update(fallback_summary(news))
            print("⚠️ Bỏ qua Gemini vì quota/API chưa khả dụng; dùng tóm tắt dự phòng.")
        else:
            try:

                result = summarize_article(news)


                # merge kết quả Gemini vào news

                if isinstance(result, dict):

                    news.update(result)



            except Exception as e:

                print(
                    "❌ Gemini error:",
                    e
                )

                news.update(fallback_summary(news))
                if is_quota_error(e):
                    gemini_unavailable = True
                    print("⚠️ Gemini đã hết quota; các bài còn lại sẽ dùng tóm tắt dự phòng.")



        # =========================
        # 5. Save database
        # =========================

        save_news(news)



        new_news.append(news)



    print(
        "\n✅ New news:",
        len(new_news)
    )



    # Bao gồm cả các bài đã lưu ở lần chạy trước nhưng Telegram chưa nhận được.
    return get_unsent_news()





if __name__ == "__main__":


    results = run_pipeline()



    for item in results:

        print("\n----------------")

        print(
            item
        )
