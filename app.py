import os
import logging
import asyncio
import random
import string
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)
from telegram.constants import ParseMode

# ========== КОНФИГУРАЦИЯ ==========
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8538212357:AAHWsvcYOsccLcI-m9C3XI1lPd19I1fszfE")
OWNER_ID = int(os.environ.get("OWNER_ID", 8294608065))
PORT = int(os.environ.get("PORT", 5000))

# Простая база данных в памяти (для демонстрации)
users_db = {}
orders_db = {}
mirror_bots_db = {}
support_tickets_db = {}

# Цены
PRICES = {
    'site_easy': 49,
    'site_hard': 69,
    'bot': 99
}

# ========== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ==========
def generate_unique_id():
    """Генерация уникального ID вида W-123456"""
    return f"W-{random.randint(100000, 999999)}"

def generate_order_id():
    """Генерация ID заказа"""
    return str(random.randint(100000, 999999))

def get_user(user_id):
    """Получение пользователя"""
    if user_id not in users_db:
        return None
    return users_db[user_id]

def create_user(user_id, username, first_name):
    """Создание пользователя"""
    users_db[user_id] = {
        'user_id': user_id,
        'username': username,
        'first_name': first_name,
        'unique_id': generate_unique_id(),
        'balance': 0,
        'is_banned': False,
        'ban_reason': None,
        'ban_until': None,
        'created_at': datetime.now()
    }
    return users_db[user_id]

def get_or_create_user(user_id, username, first_name):
    """Получение или создание пользователя"""
    user = get_user(user_id)
    if not user:
        user = create_user(user_id, username, first_name)
    return user

# ========== КЛАВИАТУРЫ ==========
def get_main_keyboard():
    """Главное меню"""
    keyboard = [
        [InlineKeyboardButton("👤 Профиль", callback_data='profile')],
        [InlineKeyboardButton("📦 Каталог", callback_data='catalog')],
        [InlineKeyboardButton("🛟 Поддержка", callback_data='support')],
        [InlineKeyboardButton("🪞 Создать зеркало", callback_data='create_mirror')],
        [InlineKeyboardButton("📋 Список зеркал", callback_data='mirror_list')]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_catalog_keyboard():
    """Каталог"""
    keyboard = [
        [InlineKeyboardButton("🌐 Сайт от 49₽", callback_data='catalog_sites')],
        [InlineKeyboardButton("🤖 Telegram Bot - 99₽", callback_data='buy_bot')],
        [InlineKeyboardButton("📱 Приложение", callback_data='app')],
        [InlineKeyboardButton("◀️ Назад", callback_data='back_to_main')]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_sites_keyboard():
    """Типы сайтов"""
    keyboard = [
        [InlineKeyboardButton("Сайт (Easy) - 49₽", callback_data='buy_site_easy')],
        [InlineKeyboardButton("Сайт (Hard) - 69₽", callback_data='buy_site_hard')],
        [InlineKeyboardButton("◀️ Назад", callback_data='back_to_catalog')]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_payment_keyboard():
    """Пополнение баланса"""
    keyboard = [
        [InlineKeyboardButton("💳 Оплатить", url="https://pay.cloudtips.ru/p/5fb41094")],
        [InlineKeyboardButton("◀️ Назад", callback_data='profile')]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_cancel_keyboard():
    """Отмена"""
    keyboard = [
        [InlineKeyboardButton("❌ Отмена", callback_data='cancel_order')]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_back_keyboard():
    """Назад"""
    keyboard = [
        [InlineKeyboardButton("◀️ Назад", callback_data='back_to_main')]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_confirm_keyboard(order_id):
    """Подтверждение заказа"""
    keyboard = [
        [
            InlineKeyboardButton("✅ Да", callback_data=f'confirm_{order_id}'),
            InlineKeyboardButton("❌ Нет", callback_data=f'reject_{order_id}')
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

# ========== ОБРАБОТЧИКИ КОМАНД ==========
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик /start"""
    user = update.effective_user
    user_data = get_or_create_user(user.id, user.username, user.first_name)
    
    if user_data['is_banned']:
        await update.message.reply_text("🚫 Вы забанены в системе.")
        return
    
    welcome_text = (
        "Привет! Я Web-Nify! Создаю сайты, телеграм боты, "
        "а также из редко приложения для десктопа или мобайл."
    )
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=get_main_keyboard()
    )

async def addmoney_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /addmoney"""
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ Нет прав!")
        return
    
    if len(context.args) != 2:
        await update.message.reply_text("Использование: /addmoney [ID] [сумма]")
        return
    
    unique_id = context.args[0]
    try:
        amount = int(context.args[1])
    except:
        await update.message.reply_text("❌ Неверная сумма!")
        return
    
    # Ищем пользователя
    user = None
    for u in users_db.values():
        if u['unique_id'] == unique_id:
            user = u
            break
    
    if not user:
        await update.message.reply_text("❌ Пользователь не найден!")
        return
    
    user['balance'] += amount
    await update.message.reply_text(f"✅ Баланс пополнен на {amount}₽")
    
    # Уведомляем пользователя
    try:
        await context.bot.send_message(
            user['user_id'],
            f"💰 Ваш баланс пополнен на {amount}₽!\nThanks For Donating!"
        )
    except:
        pass

async def cancelsell_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /cancelsell"""
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ Нет прав!")
        return
    
    if len(context.args) < 2:
        await update.message.reply_text("Использование: /cancelsell [номер] [причина]")
        return
    
    order_id = context.args[0]
    reason = ' '.join(context.args[1:])
    
    if order_id not in orders_db:
        await update.message.reply_text("❌ Заказ не найден!")
        return
    
    order = orders_db[order_id]
    user = get_user(order['user_id'])
    
    if user:
        user['balance'] += order['price']
    
    # Удаляем заказ
    del orders_db[order_id]
    
    await update.message.reply_text(f"✅ Заказ отменен!")
    
    # Уведомляем пользователя
    try:
        await context.bot.send_message(
            order['user_id'],
            f"❌ Заказ отменен!\nПричина: {reason}\nДеньги возвращены."
        )
    except:
        pass

async def editbalance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /editbalance"""
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ Нет прав!")
        return
    
    if len(context.args) != 2:
        await update.message.reply_text("Использование: /editbalance [ID] [сумма]")
        return
    
    unique_id = context.args[0]
    try:
        amount = int(context.args[1])
    except:
        await update.message.reply_text("❌ Неверная сумма!")
        return
    
    # Ищем пользователя
    user = None
    for u in users_db.values():
        if u['unique_id'] == unique_id:
            user = u
            break
    
    if not user:
        await update.message.reply_text("❌ Пользователь не найден!")
        return
    
    user['balance'] = amount
    await update.message.reply_text(f"✅ Баланс установлен: {amount}₽")

async def nulluser_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /nulluser"""
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ Нет прав!")
        return
    
    if len(context.args) < 1:
        await update.message.reply_text("Использование: /nulluser [ID] [причина]")
        return
    
    unique_id = context.args[0]
    reason = ' '.join(context.args[1:]) if len(context.args) > 1 else "Не указана"
    
    # Ищем пользователя
    user = None
    for u in users_db.values():
        if u['unique_id'] == unique_id:
            user = u
            break
    
    if not user:
        await update.message.reply_text("❌ Пользователь не найден!")
        return
    
    # Обнуляем
    user['balance'] = 0
    user['unique_id'] = generate_unique_id()
    
    await update.message.reply_text(f"✅ Аккаунт обнулен!")
    
    # Уведомляем пользователя
    try:
        await context.bot.send_message(
            user['user_id'],
            f"🔄 Аккаунт обнулен!\nПричина: {reason}"
        )
    except:
        pass

async def banuser_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /banuser"""
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ Нет прав!")
        return
    
    if len(context.args) < 3:
        await update.message.reply_text("Использование: /banuser [ID] [причина] [дни]")
        return
    
    unique_id = context.args[0]
    reason = context.args[1]
    
    try:
        days = int(context.args[2])
    except:
        await update.message.reply_text("❌ Неверный срок!")
        return
    
    # Ищем пользователя
    user = None
    for u in users_db.values():
        if u['unique_id'] == unique_id:
            user = u
            break
    
    if not user:
        await update.message.reply_text("❌ Пользователь не найден!")
        return
    
    if days == -1:
        user['is_banned'] = True
        ban_text = "навсегда"
    else:
        user['ban_until'] = datetime.now() + timedelta(days=days)
        ban_text = f"на {days} дней"
    
    user['ban_reason'] = reason
    
    await update.message.reply_text(f"✅ Пользователь забанен!")
    
    # Уведомляем пользователя
    try:
        await context.bot.send_message(
            user['user_id'],
            f"🚫 Заблокирован {ban_text}\nПричина: {reason}"
        )
    except:
        pass

async def usersid_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /usersid"""
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ Нет прав!")
        return
    
    if not users_db:
        await update.message.reply_text("📭 Пользователей нет")
        return
    
    text = "📋 Список пользователей:\n\n"
    for i, user in enumerate(users_db.values(), 1):
        status = "🚫" if user['is_banned'] else "✅"
        text += f"{i}. {user['first_name']} - {user['unique_id']} - {user['balance']}₽ {status}\n"
    
    await update.message.reply_text(text)

# ========== ОБРАБОТЧИКИ CALLBACK ==========
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик кнопок"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user = get_or_create_user(user_id, query.from_user.username, query.from_user.first_name)
    
    if user['is_banned']:
        await query.edit_message_text("🚫 Вы забанены!")
        return
    
    # Главное меню
    if query.data == 'profile':
        await show_profile(query, user)
    elif query.data == 'catalog':
        await show_catalog(query)
    elif query.data == 'support':
        await request_support(query)
    elif query.data == 'create_mirror':
        await create_mirror(query)
    elif query.data == 'mirror_list':
        await show_mirror_list(query, user_id)
    elif query.data == 'back_to_main':
        await back_to_main(query)
    
    # Каталог
    elif query.data == 'catalog_sites':
        await show_sites_catalog(query)
    elif query.data == 'buy_bot':
        await initiate_purchase(query, 'bot', PRICES['bot'])
    elif query.data == 'buy_site_easy':
        await initiate_purchase(query, 'site_easy', PRICES['site_easy'])
    elif query.data == 'buy_site_hard':
        await initiate_purchase(query, 'site_hard', PRICES['site_hard'])
    elif query.data == 'app':
        await show_app_info(query)
    elif query.data == 'back_to_catalog':
        await show_catalog(query)
    
    # Покупки
    elif query.data.startswith('confirm_'):
        order_id = query.data.replace('confirm_', '')
        await confirm_order(query, order_id, context)
    elif query.data.startswith('reject_'):
        order_id = query.data.replace('reject_', '')
        context.user_data['rejecting'] = order_id
        await query.edit_message_text(f"Введите причину отмены заказа #{order_id}:")
    elif query.data == 'cancel_order':
        await query.edit_message_text("❌ Заказ отменен!", reply_markup=get_main_keyboard())
    
    # Пополнение
    elif query.data == 'deposit':
        await show_deposit(query, user)

async def show_profile(query, user):
    """Показать профиль"""
    text = (
        f"👤 *Профиль*\n\n"
        f"*Имя:* {user['first_name']}\n"
        f"*ID:* `{user['unique_id']}`\n"
        f"*Баланс:* {user['balance']}₽"
    )
    
    keyboard = [
        [InlineKeyboardButton("💳 Пополнить", callback_data='deposit')],
        [InlineKeyboardButton("◀️ Назад", callback_data='back_to_main')]
    ]
    
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN
    )

async def show_deposit(query, user):
    """Пополнение баланса"""
    payment_text = f"Пополнение баланса для: {user['user_id']}"
    feedback_text = f"Пополнение {user['unique_id']}"
    
    text = (
        f"💳 *Пополнение баланса*\n\n"
        f"В сообщении укажите:\n`{payment_text}`\n\n"
        f"В обратной связи:\n`{feedback_text}`\n\n"
        f"После оплаты ожидайте проверки."
    )
    
    await query.edit_message_text(
        text,
        reply_markup=get_payment_keyboard(),
        parse_mode=ParseMode.MARKDOWN
    )

async def show_catalog(query):
    """Каталог"""
    await query.edit_message_text(
        "📦 *Каталог услуг*\n\nВыберите:",
        reply_markup=get_catalog_keyboard(),
        parse_mode=ParseMode.MARKDOWN
    )

async def request_support(query):
    """Поддержка"""
    await query.edit_message_text(
        "🛟 *Поддержка*\n\nНапишите текст обращения:",
        reply_markup=get_back_keyboard(),
        parse_mode=ParseMode.MARKDOWN
    )
    # Устанавливаем флаг ожидания
    query.from_user.id in context.user_data or context.user_data.update({})
    context.user_data[query.from_user.id] = {'waiting_support': True}

async def create_mirror(query):
    """Создание зеркала"""
    text = (
        "🪞 *Создание зеркала*\n\n"
        "1. Создайте бота в @BotFather\n"
        "2. Получите токен\n"
        "3. Нажмите кнопку ниже"
    )
    
    keyboard = [
        [InlineKeyboardButton("У меня есть токен", callback_data='has_token')],
        [InlineKeyboardButton("◀️ Назад", callback_data='back_to_main')]
    ]
    
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN
    )

async def show_mirror_list(query, user_id):
    """Список зеркал"""
    user_bots = [b for b in mirror_bots_db.values() if b['user_id'] == user_id]
    
    if not user_bots:
        await query.edit_message_text(
            "Нет зеркальных ботов",
            reply_markup=get_back_keyboard()
        )
        return
    
    text = "📋 *Ваши зеркала:*\n\n"
    for bot in user_bots:
        text += f"• Токен: `{bot['token'][:10]}...`\n"
    
    await query.edit_message_text(
        text,
        reply_markup=get_back_keyboard(),
        parse_mode=ParseMode.MARKDOWN
    )

async def show_sites_catalog(query):
    """Каталог сайтов"""
    await query.edit_message_text(
        "🌐 *Разработка сайтов*\n\nВыберите тип:",
        reply_markup=get_sites_keyboard(),
        parse_mode=ParseMode.MARKDOWN
    )

async def initiate_purchase(query, service_type, price):
    """Начало покупки"""
    user = get_user(query.from_user.id)
    
    if user['balance'] < price:
        await query.edit_message_text(
            f"❌ Недостаточно средств!\nНужно: {price}₽\nУ вас: {user['balance']}₽",
            reply_markup=get_back_keyboard()
        )
        return
    
    # Сохраняем данные для покупки
    query.from_user.id in context.user_data or context.user_data.update({})
    context.user_data[query.from_user.id] = {
        'buying': service_type,
        'price': price
    }
    
    service_names = {
        'site_easy': "Сайт (Easy) - 49₽",
        'site_hard': "Сайт (Hard) - 69₽",
        'bot': "Telegram Bot - 99₽"
    }
    
    await query.edit_message_text(
        f"✅ {service_names[service_type]}\n\nВведите пожелания:",
        reply_markup=get_cancel_keyboard()
    )

async def show_app_info(query):
    """Информация о приложениях"""
    await query.edit_message_text(
        "📱 *Приложения*\n\nДля заказа напишите @webnify",
        reply_markup=get_back_keyboard(),
        parse_mode=ParseMode.MARKDOWN
    )

async def back_to_main(query):
    """Главное меню"""
    text = (
        "Привет! Я Web-Nify! Создаю сайты, телеграм боты, "
        "а также из редко приложения для десктопа или мобайл."
    )
    await query.edit_message_text(text, reply_markup=get_main_keyboard())

async def confirm_order(query, order_id, context):
    """Подтверждение заказа"""
    if order_id not in orders_db:
        await query.answer("Заказ не найден!")
        return
    
    order = orders_db[order_id]
    
    # Уведомляем пользователя
    try:
        await context.bot.send_message(
            order['user_id'],
            "✅ Специалист приступил к выполнению!"
        )
    except:
        pass
    
    await query.edit_message_text(
        f"✅ Заказ #{order_id} принят!",
        reply_markup=get_back_keyboard()
    )

# ========== ОБРАБОТЧИК СООБЩЕНИЙ ==========
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка текстовых сообщений"""
    user_id = update.message.from_user.id
    text = update.message.text
    user = get_or_create_user(user_id, update.message.from_user.username, update.message.from_user.first_name)
    
    if user['is_banned']:
        await update.message.reply_text("🚫 Вы забанены!")
        return
    
    # Обработка поддержки
    if user_id in context.user_data and context.user_data[user_id].get('waiting_support'):
        ticket_id = str(random.randint(1000, 9999))
        support_tickets_db[ticket_id] = {
            'user_id': user_id,
            'message': text,
            'status': 'open'
        }
        
        # Отправляем владельцу
        try:
            await context.bot.send_message(
                OWNER_ID,
                f"📩 *Новое обращение!*\n\n"
                f"От: {user['unique_id']} ({user_id})\n"
                f"Текст: {text}",
                parse_mode=ParseMode.MARKDOWN
            )
        except:
            pass
        
        await update.message.reply_text(
            "✅ Обращение отправлено!",
            reply_markup=get_main_keyboard()
        )
        context.user_data.pop(user_id, None)
    
    # Обработка покупки
    elif user_id in context.user_data and context.user_data[user_id].get('buying'):
        service_type = context.user_data[user_id]['buying']
        price = context.user_data[user_id]['price']
        
        # Проверяем баланс
        if user['balance'] < price:
            await update.message.reply_text("❌ Недостаточно средств!")
            context.user_data.pop(user_id, None)
            return
        
        # Списываем деньги
        user['balance'] -= price
        
        # Создаем заказ
        order_id = generate_order_id()
        orders_db[order_id] = {
            'order_id': order_id,
            'user_id': user_id,
            'service_type': service_type,
            'description': text,
            'price': price,
            'status': 'pending'
        }
        
        service_names = {
            'site_easy': "Сайт (Easy) - 49₽",
            'site_hard': "Сайт (Hard) - 69₽",
            'bot': "Telegram Bot - 99₽"
        }
        
        # Отправляем владельцу
        try:
            await context.bot.send_message(
                OWNER_ID,
                f"🛒 *Новый заказ!*\n\n"
                f"Услуга: {service_names[service_type]}\n"
                f"От: {user['unique_id']} ({user_id})\n"
                f"Номер: #{order_id}\n"
                f"Пожелания: {text}\n\n"
                f"Приступаем?",
                reply_markup=get_confirm_keyboard(order_id),
                parse_mode=ParseMode.MARKDOWN
            )
        except Exception as e:
            print(f"Ошибка отправки владельцу: {e}")
        
        await update.message.reply_text(
            f"✅ Заказ #{order_id} создан!\nОжидайте подтверждения.",
            reply_markup=get_main_keyboard()
        )
        context.user_data.pop(user_id, None)
    
    # Обработка причины отмены
    elif user_id == OWNER_ID and 'rejecting' in context.user_data.get(user_id, {}):
        order_id = context.user_data[user_id]['rejecting']
        
        if order_id in orders_db:
            order = orders_db[order_id]
            order_user = get_user(order['user_id'])
            
            if order_user:
                order_user['balance'] += order['price']
            
            # Уведомляем пользователя
            try:
                await context.bot.send_message(
                    order['user_id'],
                    f"❌ Заказ отменен!\nПричина: {text}\nДеньги возвращены."
                )
            except:
                pass
            
            del orders_db[order_id]
        
        await update.message.reply_text(
            f"✅ Заказ #{order_id} отменен!",
            reply_markup=get_main_keyboard()
        )
        context.user_data.pop(user_id, None)
    
    # Обработка токена зеркала
    elif user_id in context.user_data and context.user_data[user_id].get('waiting_token'):
        mirror_bots_db[text] = {
            'token': text,
            'user_id': user_id,
            'created_at': datetime.now()
        }
        
        await update.message.reply_text(
            "✅ Зеркальный бот активирован!",
            reply_markup=get_main_keyboard()
        )
        context.user_data.pop(user_id, None)

# ========== ГЛАВНАЯ ФУНКЦИЯ ==========
def main():
    """Запуск бота"""
    # Создаем приложение
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Команды
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("addmoney", addmoney_command))
    application.add_handler(CommandHandler("cancelsell", cancelsell_command))
    application.add_handler(CommandHandler("editbalance", editbalance_command))
    application.add_handler(CommandHandler("nulluser", nulluser_command))
    application.add_handler(CommandHandler("banuser", banuser_command))
    application.add_handler(CommandHandler("usersid", usersid_command))
    
    # Кнопки
    application.add_handler(CallbackQueryHandler(handle_callback))
    
    # Сообщения
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Запуск
    print("🤖 Бот Web-Nify запускается...")
    application.run_polling()

if __name__ == "__main__":
    main()
