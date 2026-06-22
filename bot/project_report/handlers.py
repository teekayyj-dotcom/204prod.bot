# pyrefly: ignore [missing-import]
from telegram import Update
# pyrefly: ignore [missing-import]
from telegram.ext import ContextTypes
from database.db import get_db_pool, get_total_cost

async def task_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Placeholder for /task command."""
    await update.message.reply_text("Tính năng cập nhật tiến độ dự án đang được phát triển.")

async def report_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Report the total aggregated costs."""
    try:
        pool = await get_db_pool()
        total_cost = await get_total_cost(pool)
        await update.message.reply_text(f"📊 **BÁO CÁO TỔNG QUAN**\n\nTổng chi phí đã ghi nhận: {total_cost:,.0f} VNĐ", parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text("❌ Không thể lấy dữ liệu báo cáo lúc này.")
