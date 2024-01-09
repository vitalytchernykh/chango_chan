import os
import asyncio
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiologger.loggers.json import JsonLogger
from logging import INFO, DEBUG

dp = Dispatcher()

@dp.message(Command('start'))
async def command_handler(message: types.Message):
  await message.answer('Привет! Как поживаешь?')

@dp.message()
async def text_handler(message: types.Message):
  # remove lead slash
  user_text = message.text[1:]
  # 
  async with app_content['hf_session'].post(
      url = app_content['HF_API_URL'],
      headers = app_content['hf_headers'],
      json = user_text) as response:
    # log event
    await app_content['cc-tg-bot-logger'].info(
        'hf model API request:\n{} {} {} {}'.format(
            response.method,
            response.url,
            response.status,
            response.reason))
    try:
      response_data = await response.json()
      generated_text = response_data[0]['generated_text']
      # log event
      await app_content['cc-tg-bot-logger'].info(
          'hf model API response payload:\n {}'.format(
              generated_text))
      # try get second line
      if '\n' in generated_text:
        generated_text = generated_text.split('\n')[1][2:]
      await message.reply(generated_text)
    except KeyError:
      await message.reply(
          'Нету ответа, давай еще раз\n{} {}'.format(
              response.status,
              response.reason))
      # log event
      app_content['logger'].error(
          'hf model API payload parsing error: {}'.format(
            response))
    except asyncio.TimeoutError:
      await message.reply(
          'Таймаут, давай еще раз\n{} {}'.format(
              response.status,
              response.reason))
      # log event
      app_content['logger'].info(
          'hf model API request error:\n{}'.format(
              response))

async def main():
  ''' init content manager
     polling events'''
  # one session for all requests
  app_content['hf_session'] = aiohttp.ClientSession()
  app_content['hf_model_name'] = 'Den4ikAI/rugpt3_2ch'
  app_content['HF_API_URL'] = 'https://api-inference.huggingface.co/models/{}'.format(
      app_content['hf_model_name'])
  app_content['hf_headers'] = {'Authorization': 'Bearer {}'.format(
      os.environ['HF_TOKEN'])}
  app_content['cc_tg_bot'] = Bot(token = os.environ['CC_TG_TOKEN'])
  app_content['cc-tg-bot-logger'] = JsonLogger.with_default_handlers(
      name='cc-tg-bot-logger',
      level = INFO)
  
  await dp.start_polling(app_content['cc_tg_bot'])

if __name__ == '__main__':
  ''' start tg bot app
    '''
app_content = {}
asyncio.run(main())
# close session on exit, please-please!
app_content['hf_session'].close()
