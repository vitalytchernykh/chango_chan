import asyncio
from aiohttp import ClientSession
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from os import environ
from aiologger.loggers.json import JsonLogger
from logging import INFO, DEBUG

dp = Dispatcher()

@dp.message(Command('start'))
async def command_handler(message: types.Message):
  ''' handle /start command
  '''
  await message.answer('Привет! Как поживаешь?')

@dp.message()
async def text_handler(message: types.Message):
  ''' handle text message
  huggingface.co model backend request '''
  # remove user question string lead slash
  user_text = message.text[1:]
  # huggingface.co model backend request
  async with app_content['hf_session'].post(
      url = app_content['HF_API_URL'],
      headers = app_content['hf_headers'],
      json = user_text) as response:
    # log event
    await app_content['cc-tg-bot-logger'].info(
        '{} model API request:{} {} {} {}'.format(
            app_content['hf_model_name'],
            response.method,
            response.url,
            response.status,
            response.reason))
    try:
      response_data = await response.json()
      generated_text = response_data[0]['generated_text']
      # log event
      await app_content['cc-tg-bot-logger'].info(
          '{} model API response payload:{}'.format(
              app_content['hf_model_name'],
              generated_text))
      # try get response payload second line
      if '\n' in generated_text:
        generated_text = generated_text.split('\n')[1][2:]
      await message.reply(generated_text)
    except KeyError:
      await message.reply(
          'Нету ответа, давай еще раз\n{} {}'.format(
              response.status,
              response.reason))
      # log event
      await app_content['cc-tg-bot-logger'].error(
          '{} model API payload parsing error:{}'.format(
            app_content['hf_model_name'],
            response))
    except asyncio.TimeoutError:
      await message.reply(
          'Таймаут, давай еще раз\n{} {}'.format(
              response.status,
              response.reason))
      # log event
      await app_content['cc-tg-bot-logger'].info(
          '{} model API request timeout:{}'.format(
              app_content['hf_model_name'],
              response))

async def main():
  ''' init content manager
  polling events '''
  # one session for all huggingface.co requests
  app_content['hf_session'] = ClientSession()
  app_content['hf_model_name'] = 'Den4ikAI/rugpt3_2ch'
  app_content['HF_API_URL'] = 'https://api-inference.huggingface.co/models/{}'.format(
      app_content['hf_model_name'])
  app_content['hf_headers'] = {'Authorization': 'Bearer {}'.format(
      environ['HF_TOKEN'])}
  app_content['cc_tg_bot'] = Bot(token = environ['CC_TG_TOKEN'])
  app_content['cc-tg-bot-logger'] = JsonLogger.with_default_handlers(
      name='cc-tg-bot-logger',
      level = INFO,
      serializer_kwargs={'ensure_ascii': False},)
  
  await dp.start_polling(app_content['cc_tg_bot'])
  # close huggingface.co session on exit, please-please!
  await app_content['hf_session'].close()

if __name__ == '__main__':
  ''' define content manager
  start tg bot app '''
app_content = {}
asyncio.run(main())
