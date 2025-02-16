import os
import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('7771401070:AAEowlF-ZGIOeAsLxA0bFlwpLnIQwCeABrM')
HUGGINGFACE_API = os.getenv('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')

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def generate_image_huggingface(prompt):
    API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
    headers = {"Authorization": f"Bearer {HUGGINGFACE_API}"}
    
    response = requests.post(API_URL, headers=headers, json={"inputs": prompt})
    
    if response.status_code != 200:
        raise Exception("Ошибка при генерации изображения")
    
    return response.content

async def generate_text(prompt):
    API_URL = "https://api-inference.huggingface.co/models/mistralai/Mixtral-8x7B-Instruct-v0.1"
    headers = {"Authorization": f"Bearer {HUGGINGFACE_API}"}
    
    response = requests.post(API_URL, headers=headers, json={
        "inputs": f"Напиши профессиональный пост для телеграм-канала о ногтевом сервисе на тему: {prompt}. Используй эмодзи. Добавь хэштеги в конце."
    })
    
    if response.status_code != 200:
        raise Exception("Ошибка при генерации текста")
        
    return response.json()[0]['generated_text']

def generate_design_prompt(theme):
    return f"professional nail art design, {theme}, elegant manicure, high-end nail salon, professional photography, soft lighting, detailed nail art, luxury beauty, instagram worthy, professional quality, 8k, hyperrealistic"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = """
    Привет! Я помогу создать контент для вашего nail-блога 💅
    
    Доступные команды:
    /salon [тема] - Сгенерировать обзор салона
    /design [тема] - Сгенерировать обзор дизайна
    /trend [тема] - Сгенерировать пост о тренде
    
    Например:
    /salon уютная студия в центре города
    /design французский маникюр с цветами
    /trend модные цвета весны 2025
    """
    await update.message.reply_text(welcome_text)

async def salon_review(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        theme = ' '.join(context.args) if context.args else "современный салон красоты"
        await update.message.reply_text("Создаю обзор салона...")
        
        # Генерируем текст обзора
        prompt = f"Напиши подробный обзор салона красоты на тему: {theme}. Включи описание интерьера, услуг, цен, преимуществ. Используй эмодзи."
        review_text = await generate_text(prompt)
        
        # Генерируем изображение салона
        image_prompt = f"luxury nail salon interior, {theme}, modern design, beauty salon, professional lighting, elegant interior, high-end equipment, 8k, hyperrealistic"
        image = await generate_image_huggingface(image_prompt)
        
        # Отправляем результаты
        await update.message.reply_photo(image)
        await update.message.reply_text(review_text)
        
    except Exception as e:
        await update.message.reply_text(f"Произошла ошибка: {str(e)}")

async def design_review(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        theme = ' '.join(context.args) if context.args else "модный маникюр"
        await update.message.reply_text("Создаю обзор дизайна...")
        
        # Генерируем текст о дизайне
        prompt = f"Напиши подробный пост о дизайне ногтей: {theme}. Опиши технику выполнения, материалы, особенности дизайна. Используй эмодзи."
        design_text = await generate_text(prompt)
        
        # Генерируем изображение дизайна
        image = await generate_image_huggingface(generate_design_prompt(theme))
        
        # Отправляем результаты
        await update.message.reply_photo(image)
        await update.message.reply_text(design_text)
        
    except Exception as e:
        await update.message.reply_text(f"Произошла ошибка: {str(e)}")

async def trend_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        theme = ' '.join(context.args) if context.args else "тренды маникюра"
        await update.message.reply_text("Создаю пост о тренде...")
        
        # Генерируем текст о тренде
        prompt = f"Напиши пост о трендах в маникюре на тему: {theme}. Включи описание тенденций, советы по применению, рекомендации. Используй эмодзи."
        trend_text = await generate_text(prompt)
        
        # Генерируем коллаж из трендовых дизайнов
        image = await generate_image_huggingface(generate_design_prompt(theme))
        
        # Отправляем результаты
        await update.message.reply_photo(image)
        await update.message.reply_text(trend_text)
        
    except Exception as e:
        await update.message.reply_text(f"Произошла ошибка: {str(e)}")

def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("salon", salon_review))
    application.add_handler(CommandHandler("design", design_review))
    application.add_handler(CommandHandler("trend", trend_post))

    application.run_polling()

if __name__ == '__main__':
    main()
