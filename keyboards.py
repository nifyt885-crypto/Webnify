from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def get_main_keyboard():
    """Клавиатура главного меню"""
    keyboard = [
        [InlineKeyboardButton("👤 Профиль", callback_data='profile')],
        [InlineKeyboardButton("📦 Каталог", callback_data='catalog')],
        [InlineKeyboardButton("🛟 Поддержка", callback_data='support')],
        [InlineKeyboardButton("🪞 Создать зеркало", callback_data='create_mirror')],
        [InlineKeyboardButton("📋 Список зеркал", callback_data='mirror_list')]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_catalog_keyboard():
    """Клавиатура каталога"""
    keyboard = [
        [InlineKeyboardButton("🌐 Сайт от 49₽", callback_data='catalog_sites')],
        [InlineKeyboardButton("🤖 Telegram Bot - 99₽", callback_data='buy_bot')],
        [InlineKeyboardButton("📱 Приложение", callback_data='app')],
        [InlineKeyboardButton("◀️ Назад", callback_data='back_to_main')]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_sites_keyboard():
    """Клавиатура выбора типа сайта"""
    keyboard = [
        [InlineKeyboardButton("Сайт (Easy) - 49₽", callback_data='buy_site_easy')],
        [InlineKeyboardButton("Сайт (Hard) - 69₽", callback_data='buy_site_hard')],
        [InlineKeyboardButton("◀️ Назад", callback_data='back_to_catalog')]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_payment_keyboard(user_id, unique_id):
    """Клавиатура для пополнения баланса"""
    payment_text = f"Пополнение баланса для: {user_id}"
    feedback_text = f"Пополнение {unique_id}"
    
    keyboard = [
        [InlineKeyboardButton("💳 Оплатить", url="https://pay.cloudtips.ru/p/5fb41094")],
        [InlineKeyboardButton("◀️ Назад", callback_data='profile')]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_cancel_keyboard():
    """Клавиатура отмены"""
    keyboard = [
        [InlineKeyboardButton("❌ Отмена", callback_data='cancel_order')]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_back_keyboard():
    """Кнопка назад"""
    keyboard = [
        [InlineKeyboardButton("◀️ Назад", callback_data='back_to_main')]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_confirm_keyboard(order_id):
    """Клавиатура подтверждения заказа для владельца"""
    keyboard = [
        [
            InlineKeyboardButton("✅ Да", callback_data=f'confirm_order_{order_id}'),
            InlineKeyboardButton("❌ Нет", callback_data=f'reject_order_{order_id}')
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_support_response_keyboard(ticket_id):
    """Клавиатура ответа на обращение в поддержку"""
    keyboard = [
        [InlineKeyboardButton("📝 Ответить", callback_data=f'respond_ticket_{ticket_id}')]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_has_token_keyboard():
    """Клавиатура для зеркального бота"""
    keyboard = [
        [InlineKeyboardButton("У меня есть токен", callback_data='has_token')],
        [InlineKeyboardButton("◀️ Назад", callback_data='back_to_main')]
    ]
    return InlineKeyboardMarkup(keyboard)