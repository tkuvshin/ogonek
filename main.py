import os
import json
import asyncio
from difflib import SequenceMatcher

import uvicorn
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import Application, ContextTypes, MessageHandler, filters
from openai import OpenAI
import httpx

app = FastAPI()

TELEGRAM_BOT_TOKEN = os.environ["Telegram_Bot_Token"]
YANDEX_OAUTH_TOKEN = os.environ["YANDEX_OAUTH_TOKEN"]
YANDEX_TABLE_ID = os.environ["YANDEX_TABLE_ID"]
client_gpt = OpenAI(api_key=os.environ["MyKey2"])

application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

async def fetch_table_records():
    url = f"https://tables.api.yandex.net/v1/tables/{YANDEX_TABLE_ID}/data"
    headers = {"Authorization": f"OAuth {YANDEX_OAUTH_TOKEN}"}
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers=headers)
        if resp.status_code != 200:
            print(f"Ошибка получения таблицы: {resp.status_code}")
            return []
        data = resp.json()
        records = []
        for row in data.get("rows", []):
            record = {}
            for i, column in enumerate(data["columns"]):
                record[column["name"]] = row["values"][i]
            records.append(record)
        return records

def find_similar_answer(user_question, records):
    user_question = user_question.strip().lower()
    best_ratio = 0
    best_answer = None
    for record in records:
        db_question = str(record.get("question", "")).strip().lower()
        ratio = SequenceMatcher(None, user_question, db_question).ratio()
        if ratio > best_ratio:
            best_ratio = ratio
            best_answer = record.get("answer", "")
    if best_ratio > 0.65:
        return best_answer
    return None

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text.strip()
    records = await fetch_table_records()
    answer = find_similar_answer(user_message, records)
    if answer:
        await update.message.reply_text(answer)
        return

    prompt = f"""
Ты-помощник по пожарной безопасности в Российской федерации, пожарный инспектор на вашей стороне.
Отвечай развернуто (3-4 предложения) простыми словами и без сложных терминов.

Вопрос пользователя: "{user_message}"

Ответ:
"""
    response = client_gpt.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Ты профессиональный консультант по пожарной безопасности."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=300,
        temperature=0.3
    )
    gpt_answer = response.choices[0].message.content.strip()
    await update.message.reply_text(gpt_answer)

application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

@app.post("/")
async def telegram_webhook(req: Request):
    data = await req.json()
    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
