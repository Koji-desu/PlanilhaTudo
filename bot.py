from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import extrator
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import string
from extensoes import db
from models import Usuario, Aposta
from telegram import ReplyKeyboardMarkup, KeyboardButton
from app import app  # certifique-se de que o nome do arquivo é mesmo app.py


# Autenticação Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credenciais.json", scope)
client = gspread.authorize(creds)
planilha = client.open("PLANILHA GANHOSEPERDAS")
aba = planilha.worksheet("Out")

# Função para inserir dados a partir da coluna J
def append_em_coluna(aba, coluna_inicial, valores):
    colunas = {letra: idx + 1 for idx, letra in enumerate(string.ascii_uppercase)}
    col_inicio = colunas.get(coluna_inicial.upper(), 1)
    ultima_linha = len(aba.col_values(col_inicio)) + 1
    for i, valor in enumerate(valores):
        aba.update_cell(ultima_linha, col_inicio + i, valor)

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot ativo! Envie uma imagem da aposta para extrair os dados.")

# Processa imagem enviada
async def processar_imagem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    foto = update.message.photo[-1]
    caminho = f"imagem_{update.message.message_id}.png"
    arquivo = await foto.get_file()
    await arquivo.download_to_drive(caminho)


    texto = extrator.extrair_texto_imagem(caminho)
    odd = extrator.extrair_odd_aposta(texto)
    aposta = extrator.extrair_valor_aposta(texto)
    retorno = extrator.extrair_valor_retorno(texto)
    data_aposta = extrator.extrair_data(texto)

    print(texto)
    print("-----------------------------------")
    print(f"Aposta: {aposta}, Retorno: {retorno}, Odd: {odd}", "Data:",{data_aposta})
    os.remove(caminho)

    if aposta == retorno:
        resultado = 'Cash Out'

    if str(retorno) == '0,00':
        resultado = 'Perda'
    else:
        resultado = 'Ganho'

    if aposta and retorno and odd:
        dados = [data_aposta, aposta, odd, resultado, retorno]
        context.user_data["dados_pendentes"] = dados
        context.user_data["texto_ocr"] = texto
        await update.message.reply_text(
            f"Aposta: {aposta}\nRetorno: {retorno}\nOdd: {odd}\nDeseja enviar para a planilha?\nUse /confirmar ou /cancelar"
        )
    else:
        await update.message.reply_text("Não consegui extrair os dados da imagem.")

# Confirma envio
async def confirmar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    dados = context.user_data.get("dados_pendentes")
    usuario_id = context.user_data.get("usuario_id")
    if not usuario_id:
        await update.message.reply_text("⚠️ Você precisa verificar seu telefone antes de usar este comando. Use /telefone.")
        return
    if dados:
        append_em_coluna(aba, 'J', dados)
        data_str = dados[0]
        data_formatada = datetime.strptime(data_str, "%d/%m/%Y").date()
        nova_aposta = Aposta(
            data=data_formatada,
            valor_aposta=dados[1],
            retorno=dados[4],
            odd=dados[2],
            resultado=dados[3], 
            usuario_id=context.user_data["usuario_id"])
        
        with app.app_context():
            db.session.add(nova_aposta)
            db.session.commit()
        await update.message.reply_text("✅ Dados enviados com sucesso!")
        context.user_data.pop("dados_pendentes", None)
    else:
        await update.message.reply_text("Não há dados pendentes para enviar.")

# Cancela envio
async def cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("❌ Envio cancelado. Os dados foram descartados.")

async def solicitar_telefone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    teclado = [[KeyboardButton("📱 Enviar telefone", request_contact=True)]]
    reply_markup = ReplyKeyboardMarkup(teclado, one_time_keyboard=True)
    await update.message.reply_text("Por favor, envie seu número de telefone:", reply_markup=reply_markup)

async def receber_telefone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contato = update.message.contact
    telefone = contato.phone_number
    print(f"📲 Telefone recebido do Telegram: {telefone}")
    with app.app_context():
        usuario = Usuario.query.filter_by(tel=telefone).first()

    if usuario:
        context.user_data["usuario_id"] = usuario.id
        await boas_vindas(update, context, usuario)
    else:
        await update.message.reply_text("❌ Telefone não encontrado. Faça cadastro no site.")

async def boas_vindas(update: Update, context: ContextTypes.DEFAULT_TYPE, usuario):
    mensagem = (
        f"👋 Olá, {usuario.nome}!\n\n"
        "Seja bem-vindo de volta ao nosso sistema de apostas. 🎯\n"
        "Você já pode enviar uma imagem da sua aposta para que eu extraia os dados automaticamente.\n\n"
        "📌 Lembre-se: após o processamento, use /confirmar para salvar na planilha e no sistema.\n"
        "Se quiser cancelar, é só usar /cancelar.\n\n"
        "Vamos nessa? 💪"
    )
    await update.message.reply_text(mensagem)


# Inicializa bot
telegram_app = ApplicationBuilder().token("8491501717:AAGA_K3A4kqpvpWwvkjiMDntMGJpb0ui_E8").build()
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CommandHandler("confirmar", confirmar))
telegram_app.add_handler(CommandHandler("cancelar", cancelar))
telegram_app.add_handler(CommandHandler("telefone", solicitar_telefone))
telegram_app.add_handler(MessageHandler(filters.CONTACT, receber_telefone))
telegram_app.add_handler(MessageHandler(filters.PHOTO, processar_imagem))
telegram_app.run_polling()
