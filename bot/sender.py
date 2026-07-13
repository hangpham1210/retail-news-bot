import asyncio
import os

from telegram import Bot
from telegram.constants import ParseMode
from telegram.error import NetworkError, TimedOut
from telegram.request import HTTPXRequest

from dotenv import load_dotenv

from src.database.history import mark_as_sent


load_dotenv()


BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


if not BOT_TOKEN:
    raise ValueError("❌ Thiếu TELEGRAM_BOT_TOKEN trong file .env")


if not CHAT_ID:
    raise ValueError("❌ Thiếu TELEGRAM_CHAT_ID trong file .env")


async def send_message_with_retry(bot, text, **kwargs):
    """Gửi Telegram với retry, trả về True chỉ khi API phản hồi thành công."""

    for attempt in range(1, 4):
        try:
            await bot.send_message(chat_id=CHAT_ID, text=text, **kwargs)
            return True

        except (TimedOut, NetworkError) as error:
            if attempt == 3:
                print(f"⚠️ Không thể gửi Telegram sau 3 lần: {error}")
                return False

            wait_seconds = attempt * 2
            print(
                f"⚠️ Telegram lỗi kết nối (lần {attempt}/3): {error}. "
                f"Thử lại sau {wait_seconds} giây."
            )
            await asyncio.sleep(wait_seconds)

        except Exception as error:
            print(f"❌ Lỗi khi gửi Telegram: {error}")
            return False



async def send_news(news):

    """
    Gửi danh sách tin lên Telegram.
    """

    request = HTTPXRequest(
        connect_timeout=20,
        read_timeout=20,
        write_timeout=20,
        pool_timeout=20,
    )
    bot = Bot(token=BOT_TOKEN, request=request)


    if not news:

        await send_message_with_retry(bot, "📭 Hôm nay không có tin mới.")

        return



    message = (
        "📰 <b>RETAIL NEWS UPDATE</b>\n\n"
    )



    for idx, article in enumerate(news, 1):


        importance = article.get(
            "importance",
            0
        )


        topic = article.get(
            "topic",
            "Khác"
        )


        summary = article.get(
            "summary",
            []
        )


        tags = article.get(
            "tags",
            []
        )


        message += (
            f"<b>{idx}. {article.get('title')}</b>\n"
            f"📰 Nguồn: {article.get('source')}\n"
            f"📌 Chủ đề: {topic}\n"
            f"⭐ Importance: {importance}/10\n\n"
        )



        if summary:

            for s in summary:

                message += f"• {s}\n"


        if tags:

            message += (
                "\n🏷 Tags: "
                + ", ".join(tags)
                + "\n"
            )


        message += (
            f"\n🔗 {article.get('link')}\n\n"
            "--------------------\n\n"
        )



    sent = await send_message_with_retry(
        bot,
        message,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )
    if sent:
        print("✅ Đã gửi Telegram thành công")
        # Chỉ đánh dấu khi Telegram đã nhận thành công.
        mark_as_sent(news)
