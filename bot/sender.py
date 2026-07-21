import asyncio
import os

from telegram import Bot
from telegram.constants import ParseMode
from telegram.error import NetworkError, TimedOut
from telegram.request import HTTPXRequest
from datetime import datetime
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


def build_message(articles, start_index, part_number, total_parts):
    """Tạo một phần bản tin Telegram, đánh số bài theo toàn bộ danh sách."""

    today = datetime.now().strftime("%d/%m/%Y")
    part_label = f" ({part_number}/{total_parts})" if total_parts > 1 else ""
    message = (
        f"📰 <b>NEWS UPDATE{part_label}</b>\n"
        f"📅 {today}\n\n"
    )

    for index, article in enumerate(articles, start_index):
        summary = article.get("summary", [])
        tags = article.get("tags", [])

        message += (
            f"<b>{index}. {article.get('title')}</b>\n"
            f"📰 Nguồn: {article.get('source')}\n\n"
            f"<b>📝 Tóm tắt</b>\n"
        )

        for item in summary:
            message += f"• {item}\n"

        if tags:
            message += "\n🏷 Tags: " + ", ".join(tags) + "\n"

        message += f"\n🔗 {article.get('link')}\n\n--------------------\n\n"

    return message



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



    # Tối đa 6 bài gửi một tin; từ 7 bài trở lên tách hai phần gần bằng nhau.
    if len(news) <= 6:
        batches = [news]
    else:
        midpoint = (len(news) + 1) // 2
        batches = [news[:midpoint], news[midpoint:]]

    start_index = 1
    for part_number, batch in enumerate(batches, 1):
        message = build_message(
            batch,
            start_index,
            part_number,
            len(batches),
        )
        sent = await send_message_with_retry(
            bot,
            message,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )

        if sent:
            print(f"✅ Đã gửi Telegram phần {part_number}/{len(batches)}")

        start_index += len(batch)
