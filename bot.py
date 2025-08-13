import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# 3 ta admin ID
ADMINS = [8194221675, 222222222, 333333333]
EMPLOYEES = [7570338476, 555555555]

# MoySklad API ma'lumotlari
MOYSKLAD_LOGIN = "abdumutalov@forge-group"
MOYSKLAD_PASSWORD = "122Komronbek"

# Token va portni olish
TOKEN = os.getenv("BOT_TOKEN")  # Render Environment Variables ichida saqlanadi
PORT = int(os.environ.get("PORT", 8443))  # Render avtomatik beradi

def check_access(user_id):
    if user_id in ADMINS:
        return "admin"
    elif user_id in EMPLOYEES:
        return "employee"
    else:
        return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    role = check_access(update.effective_user.id)
    if role == "admin":
        await update.message.reply_text("✅ Salom, ADMIN!\nQoldiq uchun /ostatki buyrug‘ini ishlating.")
    elif role == "employee":
        await update.message.reply_text("✅ Salom, Hodim!\nQoldiq uchun /ostatki buyrug‘ini ishlating.")
    else:
        await update.message.reply_text("⛔ Sizga bu botdan foydalanish ruxsati yo‘q.")

def get_moysklad_stock():
    url = "https://online.moysklad.ru/app/#stockReport?reportType=STORES"
    response = requests.get(url, auth=(MOYSKLAD_LOGIN, MOYSKLAD_PASSWORD))
    if response.status_code == 200:
        data = response.json()
        results = []
        for item in data.get('rows', []):
            name = item.get('name', 'Noma’lum')
            quantity = item.get('quantity', 0)
            results.append(f"{name} — {quantity}")
        return "\n".join(results) if results else "📭 Qoldiq topilmadi."
    else:
        return f"❌ Xato: {response.status_code}"

async def ostatki(update: Update, context: ContextTypes.DEFAULT_TYPE):
    role = check_access(update.effective_user.id)
    if role in ["admin", "employee"]:
        await update.message.reply_text("⏳ Qoldiqlar yuklanmoqda...")
        await update.message.reply_text(get_moysklad_stock())
    else:
        await update.message.reply_text("⛔ Sizga bu buyruqni ishlatish ruxsati yo‘q.")

async def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ostatki", ostatki))

    render_url = os.getenv("RENDER_EXTERNAL_URL")
    webhook_url = f"{render_url}/{TOKEN}"

    await app.bot.set_webhook(webhook_url)
    await app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TOKEN,
        webhook_url=webhook_url
    )

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
