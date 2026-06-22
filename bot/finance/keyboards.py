from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def get_cost_categories_keyboard() -> InlineKeyboardMarkup:
    """Returns the inline keyboard with cost categories."""
    keyboard = [
        [
            InlineKeyboardButton("🍕 Ăn uống", callback_data="cost_category:Ăn uống"),
            InlineKeyboardButton("🚗 Di chuyển", callback_data="cost_category:Di chuyển")
        ],
        [
            InlineKeyboardButton("🎬 Thiết bị", callback_data="cost_category:Thiết bị"),
            InlineKeyboardButton("🏠 Lưu trú", callback_data="cost_category:Lưu trú")
        ],
        [
            InlineKeyboardButton("💼 Khác", callback_data="cost_category:Khác")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_ai_confirmation_keyboard(category: str, amount: float) -> InlineKeyboardMarkup:
    """Returns the inline keyboard for AI confirmation."""
    keyboard = [
        [
            InlineKeyboardButton("✅ Chuẩn xác. Lưu ngay", callback_data=f"ai_confirm:{category}:{amount}"),
        ],
        [
            InlineKeyboardButton("❌ AI nhận diện sai, để nhập tay", callback_data="ai_reject")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)
