from telegram import Update
from telegram.ext import ContextTypes
from config import OWNER_ID
from database import Database

db = Database()

async def addmoney_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /addmoney для пополнения баланса"""
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ У вас нет прав для этой команды!")
        return
    
    if len(context.args) != 2:
        await update.message.reply_text(
            "Использование: /addmoney [уник.ID] [сумма]\n"
            "Пример: /addmoney W-123456 1000"
        )
        return
    
    unique_id = context.args[0]
    try:
        amount = int(context.args[1])
    except ValueError:
        await update.message.reply_text("❌ Неверная сумма!")
        return
    
    user = db.get_user_by_unique_id(unique_id)
    if not user:
        await update.message.reply_text("❌ Пользователь не найден!")
        return
    
    db.update_balance(user[0], amount)
    
    # Уведомляем пользователя
    from bot import application
    await application.bot.send_message(
        chat_id=user[0],
        text=f"💰 Ваш баланс пополнен на {amount}₽!\nThanks For Donating!"
    )
    
    await update.message.reply_text(
        f"✅ Баланс пользователя {unique_id} пополнен на {amount}₽"
    )

async def cancelsell_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /cancelsell для отмены заказа"""
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ У вас нет прав для этой команды!")
        return
    
    if len(context.args) < 2:
        await update.message.reply_text(
            "Использование: /cancelsell [номер_заказа] [причина]\n"
            "Пример: /cancelsell 123456 неверные требования"
        )
        return
    
    order_id = context.args[0]
    reason = ' '.join(context.args[1:])
    
    order = db.get_order(order_id)
    if not order:
        await update.message.reply_text("❌ Заказ не найден!")
        return
    
    # Возвращаем средства
    db.update_balance(order[1], order[4])  # user_id, price
    
    # Обновляем статус заказа
    db.update_order_status(order_id, 'cancelled')
    
    # Уведомляем пользователя
    from bot import application
    await application.bot.send_message(
        chat_id=order[1],
        text=f"❌ Ваш заказ отменен!\nПричина: {reason}"
    )
    
    await update.message.reply_text(
        f"✅ Заказ #{order_id} отменен, средства возвращены."
    )

async def editbalance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /editbalance для изменения баланса"""
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ У вас нет прав для этой команды!")
        return
    
    if len(context.args) != 2:
        await update.message.reply_text(
            "Использование: /editbalance [уник.ID] [сумма]\n"
            "Пример: /editbalance W-123456 500"
        )
        return
    
    unique_id = context.args[0]
    try:
        amount = int(context.args[1])
    except ValueError:
        await update.message.reply_text("❌ Неверная сумма!")
        return
    
    user = db.get_user_by_unique_id(unique_id)
    if not user:
        await update.message.reply_text("❌ Пользователь не найден!")
        return
    
    db.set_balance(user[0], amount)
    
    await update.message.reply_text(
        f"✅ Баланс пользователя {unique_id} изменен на {amount}₽"
    )

async def nulluser_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /nulluser для обнуления аккаунта"""
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ У вас нет прав для этой команды!")
        return
    
    if len(context.args) < 1:
        await update.message.reply_text(
            "Использование: /nulluser [уник.ID] [причина]\n"
            "Пример: /nulluser W-123456 нарушение правил"
        )
        return
    
    unique_id = context.args[0]
    reason = ' '.join(context.args[1:]) if len(context.args) > 1 else "Не указана"
    
    user_id = db.nullify_user(unique_id, reason)
    if not user_id:
        await update.message.reply_text("❌ Пользователь не найден!")
        return
    
    # Уведомляем пользователя
    from bot import application
    await application.bot.send_message(
        chat_id=user_id,
        text=f"🔄 Ваш аккаунт обнулён!\nПричина: {reason}"
    )
    
    await update.message.reply_text(
        f"✅ Аккаунт пользователя {unique_id} обнулен."
    )

async def banuser_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /banuser для блокировки пользователя"""
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ У вас нет прав для этой команды!")
        return
    
    if len(context.args) < 3:
        await update.message.reply_text(
            "Использование: /banuser [уник.ID] [причина] [дни]\n"
            "Пример: /banuser W-123456 спам 7\n"
            "Для вечного бана используйте -1"
        )
        return
    
    unique_id = context.args[0]
    reason = context.args[1]
    
    try:
        days = int(context.args[2])
        if days != -1 and (days < 1 or days > 1200):
            await update.message.reply_text("❌ Срок должен быть от 1 до 1200 дней или -1 для вечного бана!")
            return
    except ValueError:
        await update.message.reply_text("❌ Неверный формат срока!")
        return
    
    user = db.get_user_by_unique_id(unique_id)
    if not user:
        await update.message.reply_text("❌ Пользователь не найден!")
        return
    
    db.ban_user(unique_id, reason, days)
    
    # Уведомляем пользователя
    from bot import application
    if days == -1:
        ban_text = "Вы заблокированы навсегда"
    else:
        ban_text = f"Вы заблокированы на {days} дней"
    
    await application.bot.send_message(
        chat_id=user[0],
        text=f"🚫 {ban_text} по причине: {reason}"
    )
    
    await update.message.reply_text(
        f"✅ Пользователь {unique_id} заблокирован."
    )

async def usersid_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /usersid для получения списка пользователей"""
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ У вас нет прав для этой команды!")
        return
    
    users = db.get_all_users()
    
    if not users:
        await update.message.reply_text("📭 Пользователей пока нет.")
        return
    
    users_list = "📋 *Список пользователей:*\n\n"
    for i, user in enumerate(users, 1):
        status = "🚫 Забанен" if user[5] else "✅ Активен"
        users_list += f"{i}. {user[2] or 'Без имени'} - {user[3]} - {user[4]}₽ - {status}\n"
    
    # Разбиваем на части, если сообщение слишком длинное
    if len(users_list) > 4000:
        parts = [users_list[i:i+4000] for i in range(0, len(users_list), 4000)]
        for part in parts:
            await update.message.reply_text(part, parse_mode='Markdown')
    else:
        await update.message.reply_text(users_list, parse_mode='Markdown')