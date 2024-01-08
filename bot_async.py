import os
import logging
import asyncio
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command

logging.basicConfig(level=logging.INFO)

''' define huggingface.co model parameters
and account token data '''
#hf_model = "ai-forever/rugpt3large_based_on_gpt2"
#hf_model = 'TheBakerCat/2chan_ruGPT3_small'
hf_model = 'Den4ikAI/rugpt3_2ch'
#hf_model = 'BlackSamorez/rudialogpt3_medium_based_on_gpt2_2ch'

logging.info('huggingface.co model: {}'.format(hf_model))

API_URL = "https://api-inference.huggingface.co/models/{}".format(hf_model)
headers = {"Authorization": "Bearer {}".format(os.environ['HF_TOKEN'])
}

''' create new tg bot object
   '''
bot = Bot(token = os.environ['CC_TG_TOKEN'])
dp = Dispatcher()

''' command handler - start
   '''
@dp.message(Command('start'))
async def command_handler(message: types.Message):
    await message.answer('Привет! Как поживаешь?')

''' text handler
   '''
@dp.message()
async def text_handler(message: types.Message):
  # remove lead slash
  user_text = message.text[1:]
  async with aiohttp.ClientSession() as session:
    response = await session.post(url = API_URL, headers = headers, json = user_text)
  logging.info('{} {} {} {}'.format(response.method, response.url, response.status, response.reason))
  generated_text = await response.json()
  logging.info('payload {}'.format(generated_text))
  try:
    generated_text = generated_text[0]['generated_text']
  except KeyError:
    generated_text = 'Что-то пошло не так, апишка не ответила:\n - модель не успела загрузиться, попробуй через 10сек\n - токен протух'
    logging.error('API error: {}'.format(response))
  # get second line
  if hf_model == 'Den4ikAI/rugpt3_2ch':
    generated_text = generated_text.split('\n')[1][2:]  
  await message.reply(generated_text)

''' polling events
   '''
async def main():
  await dp.start_polling(bot)

''' start tg bot app
   '''
if __name__ == "__main__":
  asyncio.run(main())
