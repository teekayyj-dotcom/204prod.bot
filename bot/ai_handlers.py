import logging
from telegram import Update
from telegram.ext import ContextTypes
from bot.finance.ai_service import parse_expense_text, parse_expense_image
from bot.finance.keyboards import get_ai_confirmation_keyboard, get_cost_categories_keyboard
from database.db import get_db_pool, insert_cost

logger = logging.getLogger(__name__)

async def ai_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /ai command with text."""
    # text after /ai
    if not context.args:
        await update.message.reply_text("Vui lòng nhập nội dung sau lệnh /ai. Ví dụ: /ai Mua nước hết 120k")
        return
    
    text = " ".join(context.args)
    processing_msg = await update.message.reply_text("⏳ Đang nhờ AI phân tích...")
    
    data = await parse_expense_text(text)
    if not data:
        await processing_msg.edit_text("❌ AI không thể nhận diện được dữ liệu hợp lệ. Vui lòng thử lại hoặc dùng lệnh /cost.")
        return
        
    category = data.get("hang_muc")
    amount = data.get("so_tien")
    
    confirm_text = (
        f"🤖 **HỆ THỐNG NHẬN DIỆN CHI PHÍ**\n\n"
        f"Mục: {category}\n"
        f"Số tiền: {amount:,.0f} VNĐ\n\n"
        f"Vui lòng xác nhận để lưu trữ:"
    )
    
    await processing_msg.edit_text(
        text=confirm_text,
        reply_markup=get_ai_confirmation_keyboard(category, amount),
        parse_mode="Markdown"
    )

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle image uploads for receipt parsing."""
    photo_file = await update.message.photo[-1].get_file()
    
    processing_msg = await update.message.reply_text("⏳ Đang phân tích hình ảnh hóa đơn...")
    
    # Download image as bytes
    image_bytes = await photo_file.download_as_bytearray()
    
    data = await parse_expense_image(bytes(image_bytes), "image/jpeg")
    
    if not data:
        await processing_msg.edit_text("❌ AI không thể nhận diện dữ liệu từ hình ảnh này. Vui lòng chụp rõ hơn hoặc nhập tay bằng /cost.")
        return
        
    category = data.get("hang_muc")
    amount = data.get("so_tien")
    
    confirm_text = (
        f"🤖 **HỆ THỐNG NHẬN DIỆN HÓA ĐƠN**\n\n"
        f"Mục: {category}\n"
        f"Số tiền: {amount:,.0f} VNĐ\n\n"
        f"Vui lòng xác nhận để lưu trữ:"
    )
    
    await processing_msg.edit_text(
        text=confirm_text,
        reply_markup=get_ai_confirmation_keyboard(category, amount),
        parse_mode="Markdown"
    )

async def handle_ai_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle confirmation buttons from AI parsing."""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    if data.startswith("ai_confirm:"):
        _, category, amount_str = data.split(":")
        amount = float(amount_str)
        
        user_id = query.from_user.id
        username = query.from_user.username or query.from_user.first_name
        
        try:
            pool = await get_db_pool()
            await insert_cost(
                pool=pool,
                user_id=user_id,
                username=username,
                category=category,
                amount=amount,
                input_method="AI"
            )
            await query.edit_message_text(f"✅ Ghi nhận thành công!\nHạng mục: {category}\nSố tiền: {amount:,.0f} VNĐ")
        except Exception as e:
            logger.error(f"Error saving AI cost: {e}")
            await query.edit_message_text("❌ Có lỗi xảy ra khi lưu trữ vào hệ thống.")
            
    elif data == "ai_reject":
        await query.edit_message_text(
            text="AI nhận diện sai. Vui lòng chọn hạng mục bên dưới để nhập tay:",
            reply_markup=get_cost_categories_keyboard()
        )
        # Note: We just send the keyboard here. In a real scenario, clicking it will trigger the cost_conv_handler IF it's set up to catch it.
        # We need to make sure `cost_category:` pattern in cost_conv_handler entry points can catch this.
        # We'll update main.py to route this to the ConversationHandler properly.
