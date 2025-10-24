from telegram.ext import ApplicationBuilder, CommandHandler
import asyncio
import nest_asyncio

async def start(update, context):
    print("📩 Recebi /start")
    await update.message.reply_text("Bot de teste ativo!")

app = ApplicationBuilder().token("8491501717:AAGA_K3A4kqpvpWwvkjiMDntMGJpb0ui_E8").build()
app.add_handler(CommandHandler("start", start))

async def main():
    await app.run_polling()

nest_asyncio.apply()
asyncio.get_event_loop().run_until_complete(main())
