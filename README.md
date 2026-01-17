# Web-Nify Telegram Bot

Бот для оплаты услуг Web-Nify.

## Развертывание на Scalingo

### Способ 1: Через Docker (рекомендуется)

```bash
# Создайте приложение
scalingo create webnify --region osc-fr1

# Настройте переменные окружения
scalingo env-set BOT_TOKEN="8538212357:AAHWsvcYOsccLcI-m9C3XI1lPd19I1fszfE"
scalingo env-set OWNER_ID="8294608065"

# Разверните
git push scalingo master
