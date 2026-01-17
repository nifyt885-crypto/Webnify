from telegram import Update
from telegram.ext import ContextTypes, CallbackContext
from telegram.constants import ParseMode
import asyncio
from config import BOT_TOKEN, OWNER_ID, PRICES
from database import Database
from keyboards import *

db = Database()

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user = update.effective_user
    user_data = db.get_or_create_user(user.id, user.username, user.first_name)
    
    # Проверка на бан
    if user_data[5]:  # is_banned
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

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик callback-запросов"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user_data = db.get_user_by_id(user_id)
    
    # Проверка на бан
    if user_data and user_data[5]:  # is_banned
        await query.edit_message_text("🚫 Вы забанены в системе.")
        return
    
    # Главное меню
    if query.data == 'profile':
        await show_profile(query, user_data)
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
    elif query.data.startswith('confirm_order_'):
        order_id = query.data.replace('confirm_order_', '')
        await confirm_order(query, order_id)
    elif query.data.startswith('reject_order_'):
        order_id = query.data.replace('reject_order_', '')
        await reject_order(query, order_id)
    elif query.data == 'cancel_order':
        await cancel_order(query)
    
    # Зеркальные боты
    elif query.data == 'has_token':
        await request_token(query)
    
    # Поддержка
    elif query.data.startswith('respond_ticket_'):
        ticket_id = query.data.replace('respond_ticket_', '')
        context.user_data['responding_to_ticket'] = ticket_id
        await query.edit_message_text("Введите ответ на обращение:")

async def show_profile(query, user_data):
    """Показать профиль пользователя"""
    profile_text = (
        "👤 *Ваш профиль:*\n\n"
        f"*Ваше имя:* {user_data[2] or 'Не указано'}\n"
        f"*Ваш уникальный ID:* `{user_data[3]}`\n"
        f"*Ваш баланс:* {user_data[4]}₽\n"
    )
    
    keyboard = [
        [InlineKeyboardButton("💳 Пополнить баланс", callback_data='deposit')],
        [InlineKeyboardButton("◀️ Назад", callback_data='back_to_main')]
    ]
    
    await query.edit_message_text(
        profile_text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN
    )

async def show_catalog(query):
    """Показать каталог"""
    await query.edit_message_text(
        "📦 *Каталог услуг:*\n\n"
        "Выберите интересующую услугу:",
        reply_markup=get_catalog_keyboard(),
        parse_mode=ParseMode.MARKDOWN
    )

async def request_support(query):
    """Запрос обращения в поддержку"""
    await query.edit_message_text(
        "🛟 *Поддержка*\n\n"
        "Пожалуйста, напишите текст для обращения:",
        reply_markup=get_back_keyboard(),
        parse_mode=ParseMode.MARKDOWN
    )
    # Устанавливаем состояние ожидания обращения
    from bot import application
    application.user_data[query.from_user.id] = {'waiting_for_support': True}

async def create_mirror(query):
    """Создание зеркального бота"""
    instructions = (
        "🪞 *Создание зеркального бота*\n\n"
        "Для создания зеркала:\n"
        "1. Создайте своего бота в @BotFather\n"
        "2. Получите токен бота\n"
        "3. Нажмите кнопку ниже и отправьте токен\n\n"
        "После этого ваш бот станет точной копией этого бота."
    )
    
    await query.edit_message_text(
        instructions,
        reply_markup=get_has_token_keyboard(),
        parse_mode=ParseMode.MARKDOWN
    )

async def request_token(query):
    """Запрос токена для зеркального бота"""
    await query.edit_message_text(
        "Введите токен вашего бота:",
        reply_markup=get_back_keyboard()
    )
    from bot import application
    application.user_data[query.from_user.id] = {'waiting_for_token': True}

async def show_mirror_list(query, user_id):
    """Показать список зеркальных ботов"""
    bots = db.get_mirror_bots(user_id)
    
    if not bots:
        await query.edit_message_text(
            "У вас нет созданных зеркальных ботов.",
            reply_markup=get_back_keyboard()
        )
        return
    
    bot_list = "📋 *Ваши зеркальные боты:*\n\n"
    for i, bot in enumerate(bots, 1):
        bot_list += f"{i}. Токен: `{bot[0][:10]}...`\n"
        bot_list += f"   Создан: {bot[2].strftime('%d.%m.%Y %H:%M')}\n\n"
    
    await query.edit_message_text(
        bot_list,
        reply_markup=get_back_keyboard(),
        parse_mode=ParseMode.MARKDOWN
    )

async def show_sites_catalog(query):
    """Показать каталог сайтов"""
    await query.edit_message_text(
        "🌐 *Разработка сайтов:*\n\n"
        "Выберите тип сайта:",
        reply_markup=get_sites_keyboard(),
        parse_mode=ParseMode.MARKDOWN
    )

async def initiate_purchase(query, service_type, price):
    """Инициация покупки"""
    user_id = query.from_user.id
    balance = db.get_user_balance(user_id)
    
    if balance < price:
        await query.edit_message_text(
            f"❌ *Недостаточно средств!*\n\n"
            f"Стоимость: {price}₽\n"
            f"Ваш баланс: {balance}₽\n\n"
            f"Пополните баланс в профиле.",
            reply_markup=get_back_keyboard(),
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    # Устанавливаем состояние ожидания описания
    from bot import application
    application.user_data[user_id] = {
        'waiting_for_description': True,
        'service_type': service_type,
        'price': price
    }
    
    service_names = {
        'site_easy': "Сайт (Easy)",
        'site_hard': "Сайт (Hard)",
        'bot': "Telegram Bot"
    }
    
    await query.edit_message_text(
        f"✅ *{service_names.get(service_type, 'Услуга')} - {price}₽*\n\n"
        f"Введите пожелания к заказу:",
        reply_markup=get_cancel_keyboard(),
        parse_mode=ParseMode.MARKDOWN
    )

async def show_app_info(query):
    """Информация о приложениях"""
    await query.edit_message_text(
        "📱 *Разработка приложений*\n\n"
        "Для заказа приложения напишите @webnify",
        reply_markup=get_back_keyboard(),
        parse_mode=ParseMode.MARKDOWN
    )

async def back_to_main(query):
    """Вернуться в главное меню"""
    welcome_text = (
        "Привет! Я Web-Nify! Создаю сайты, телеграм боты, "
        "а также из редко приложения для десктопа или мобайл."
    )
    await query.edit_message_text(
        welcome_text,
        reply_markup=get_main_keyboard()
    )

async def cancel_order(query):
    """Отмена заказа"""
    user_id = query.from_user.id
    from bot import application
    if user_id in application.user_data:
        application.user_data[user_id].clear()
    
    await query.edit_message_text(
        "Заказ отменен.",
        reply_markup=get_main_keyboard()
    )

async def confirm_order(query, order_id):
    """Подтверждение заказа владельцем"""
    order = db.get_order(order_id)
    if not order:
        await query.answer("Заказ не найден!")
        return
    
    # Обновляем статус заказа
    db.update_order_status(order_id, 'in_progress')
    
    # Уведомляем пользователя
    from bot import application
    await application.bot.send_message(
        chat_id=order[1],  # user_id
        text="✅ Специалист приступил к выполнению заказа! Ожидайте!"
    )
    
    await query.edit_message_text(
        f"Заказ #{order_id} принят в работу!",
        reply_markup=get_back_keyboard()
    )

async def reject_order(query, order_id):
    """Отклонение заказа владельцем"""
    order = db.get_order(order_id)
    if not order:
        await query.answer("Заказ не найден!")
        return
    
    # Устанавливаем состояние ожидания причины
    from bot import application
    application.user_data[query.from_user.id] = {
        'rejecting_order': order_id
    }
    
    await query.edit_message_text(
        f"Введите причину отмены заказа #{order_id}:"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений"""
    user_id = update.message.from_user.id
    text = update.message.text
    
    # Проверка на бан
    user_data = db.get_user_by_id(user_id)
    if user_data and user_data[5]:  # is_banned
        await update.message.reply_text("🚫 Вы забанены в системе.")
        return
    
    # Обработка поддержки
    if 'waiting_for_support' in context.user_data:
        ticket_id = db.create_support_ticket(user_id, text)
        
        # Отправляем владельцу
        from bot import application
        await application.bot.send_message(
            chat_id=OWNER_ID,
            text=f"📩 *Новое обращение в поддержку!*\n\n"
                 f"От: {user_data[3]} ({user_id})\n"
                 f"Обращение: {text}",
            reply_markup=get_support_response_keyboard(ticket_id),
            parse_mode=ParseMode.MARKDOWN
        )
        
        await update.message.reply_text(
            "✅ Ваше обращение отправлено в поддержку!",
            reply_markup=get_main_keyboard()
        )
        context.user_data.clear()
    
    # Обработка токена зеркального бота
    elif 'waiting_for_token' in context.user_data:
        if db.add_mirror_bot(user_id, text):
            await update.message.reply_text(
                "✅ Токен успешно добавлен! Ваш зеркальный бот активирован.",
                reply_markup=get_main_keyboard()
            )
        else:
            await update.message.reply_text(
                "❌ Ошибка при добавлении токена. Возможно, он уже используется.",
                reply_markup=get_main_keyboard()
            )
        context.user_data.clear()
    
    # Обработка описания заказа
    elif 'waiting_for_description' in context.user_data:
        service_type = context.user_data['service_type']
        price = context.user_data['price']
        
        # Проверяем баланс еще раз
        balance = db.get_user_balance(user_id)
        if balance < price:
            await update.message.reply_text(
                f"❌ Недостаточно средств! Нужно {price}₽, у вас {balance}₽",
                reply_markup=get_main_keyboard()
            )
            context.user_data.clear()
            return
        
        # Списываем средства
        db.update_balance(user_id, -price)
        
        # Создаем заказ
        order_id = db.create_order(user_id, service_type, text, price)
        
        # Отправляем владельцу
        service_names = {
            'site_easy': "Сайт (Easy) - 49₽",
            'site_hard': "Сайт (Hard) - 69₽",
            'bot': "Telegram Bot - 99₽"
        }
        
        from bot import application
        await application.bot.send_message(
            chat_id=OWNER_ID,
            text=f"🛒 *Новый заказ!*\n\n"
                 f"*Услуга:* {service_names.get(service_type, service_type)}\n"
                 f"*От:* {user_data[3]} ({user_id})\n"
                 f"*Номер заказа:* #{order_id}\n"
                 f"*Пожелания:* {text}\n\n"
                 f"Приступаем?",
            reply_markup=get_confirm_keyboard(order_id),
            parse_mode=ParseMode.MARKDOWN
        )
        
        await update.message.reply_text(
            f"✅ Заказ #{order_id} создан!\n"
            f"Ожидайте подтверждения от специалиста.",
            reply_markup=get_main_keyboard()
        )
        context.user_data.clear()
    
    # Обработка причины отмены заказа
    elif 'rejecting_order' in context.user_data:
        order_id = context.user_data['rejecting_order']
        order = db.get_order(order_id)
        
        if order:
            # Возвращаем средства
            db.update_balance(order[1], order[4])  # user_id, price
            
            # Обновляем статус заказа
            db.update_order_status(order_id, 'cancelled')
            
            # Уведомляем пользователя
            from bot import application
            await application.bot.send_message(
                chat_id=order[1],
                text=f"❌ Специалист отменил вашу покупку!\n"
                     f"Деньги возвращены.\n"
                     f"Причина: {text}"
            )
        
        await update.message.reply_text(
            f"Заказ #{order_id} отменен.",
            reply_markup=get_main_keyboard()
        )
        context.user_data.clear()
    
    # Обработка ответа на обращение в поддержку
    elif 'responding_to_ticket' in context.user_data and user_id == OWNER_ID:
        ticket_id = context.user_data['responding_to_ticket']
        ticket = db.get_support_ticket(ticket_id)
        
        if ticket:
            # Отправляем ответ пользователю
            from bot import application
            await application.bot.send_message(
                chat_id=ticket[6],  # user_telegram_id
                text=f"📨 *Ответ от агента поддержки:*\n\n{text}"
            )
            
            # Сохраняем ответ в БД
            db.respond_to_ticket(ticket_id, text)
            
            await update.message.reply_text(
                "✅ Ответ отправлен пользователю!",
                reply_markup=get_main_keyboard()
            )
        else:
            await update.message.reply_text("❌ Обращение не найдено!")
        
        context.user_data.clear()