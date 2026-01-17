import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from config import BOT_TOKEN
import handlers
import admin

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    """Основная функция запуска бота"""
    # Создаем приложение
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Регистрируем обработчики команд
    application.add_handler(CommandHandler("start", handlers.start_command))
    application.add_handler(CommandHandler("addmoney", admin.addmoney_command))
    application.add_handler(CommandHandler("cancelsell", admin.cancelsell_command))
    application.add_handler(CommandHandler("editbalance", admin.editbalance_command))
    application.add_handler(CommandHandler("nulluser", admin.nulluser_command))
    application.add_handler(CommandHandler("banuser", admin.banuser_command))
    application.add_handler(CommandHandler("usersid", admin.usersid_command))
    
    # Регистрируем обработчики callback-запросов
    application.add_handler(CallbackQueryHandler(handlers.handle_callback))
    
    # Регистрируем обработчик текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.handle_message))
    
    # Запускаем бота
    print("Бот запущен...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()