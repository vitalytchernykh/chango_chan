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
  try:
    response_data = await asyncio.wait_for(response.json(), timeout = 10)
    generated_text = response_data[0]['generated_text']
    logging.info('payload:\n {}'.format(generated_text))
    # try get second line
    if '\n' in generated_text:
      generated_text = generated_text.split('\n')[1][2:]
    await message.reply(generated_text)
  except asyncio.TimeoutError:
    logging.info('model API request error: {}'.format(response))
    await message.answer('Таймаут, давай еще раз\n{} {}'.format(response.status, response.reason))
  except KeyError:
    logging.error('payload parsing error: {}'.format(response))
    await message.answer('Нету ответа, давай еще раз\n{} {}'.format(response.status, response.reason))

''' polling events
   '''
async def main():
  await dp.start_polling(bot)

''' start tg bot app
   '''
if __name__ == "__main__":
  asyncio.run(main())
