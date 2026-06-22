import logging
from telegram import Update
from telegram.ext import (
    ContextTypes,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ConversationHandler,
)
from database.db import get_db_pool, insert_cost
from bot.finance.keyboards import get_cost_categories_keyboard

logger = logging.getLogger(__name__)

SELECT_CATEGORY, ENTER_AMOUNT = range(2)

async def cost_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Entry point for the manual cost logging flow."""
    await update.message.reply_text(
        "Vui lòng chọn hạng mục chi phí:",
        reply_markup=get_cost_categories_keyboard()
    )
    return SELECT_CATEGORY

async def handle_category_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles the user's category selection."""
    query = update.callback_query
    await query.answer()
    
    # Callback data format: cost_category:CategoryName
    category = query.data.split(":")[1]
    context.user_data['selected_category'] = category
    
    await query.edit_message_text(
        text=f"Bạn đã chọn: *{category}*.\nVui lòng nhập số tiền chi (chỉ nhập số, ví dụ: 500000):",
        parse_mode='Markdown'
    )
    return ENTER_AMOUNT

async def handle_amount_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles the user's amount input and saves to database."""
    text = update.message.text
    category = context.user_data.get('selected_category')
    
    try:
        amount = float(text.replace(',', '').replace('.', ''))
    except ValueError:
        await update.message.reply_text("Số tiền không hợp lệ. Vui lòng nhập lại (chỉ nhập số):")
        return ENTER_AMOUNT
    
    user_id = update.message.from_user.id
    username = update.message.from_user.username or update.message.from_user.first_name
    
    # Save to database
    try:
        pool = await get_db_pool()
        await insert_cost(
            pool=pool,
            user_id=user_id,
            username=username,
            category=category,
            amount=amount,
            input_method="Manual"
        )
        
        await update.message.reply_text(
            f"✅ Ghi nhận thành công!\n"
            f"Hạng mục: {category}\n"
            f"Số tiền: {amount:,.0f} VNĐ"
        )
    except Exception as e:
        logger.error(f"Error saving cost: {e}")
        await update.message.reply_text("❌ Có lỗi xảy ra khi lưu trữ vào hệ thống.")
    
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    await update.message.reply_text("Đã hủy thao tác ghi nhận chi phí.")
    return ConversationHandler.END

# Define the conversation handler
cost_conv_handler = ConversationHandler(
    entry_points=[
        CommandHandler('cost', cost_command),
        CallbackQueryHandler(handle_category_selection, pattern="^cost_category:")
    ],
    states={
        SELECT_CATEGORY: [
            CallbackQueryHandler(handle_category_selection, pattern="^cost_category:")
        ],
        ENTER_AMOUNT: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_amount_input)
        ],
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)
