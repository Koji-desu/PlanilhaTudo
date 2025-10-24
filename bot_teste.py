from telegram.ext import ApplicationBuilder, CommandHandler
from telegram import Update
from telegram.ext import ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Bot está online!")

app = ApplicationBuilder().token("8491501717:AAGA_K3A4kqpvpWwvkjiMDntMGJpb0ui_E8").build()
app.add_handler(CommandHandler("start", start))

if __name__ == "__main__":
    app.run_polling()
