import asyncio
from os import environ

from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiohttp import ClientSession

import modules.chatBot

dp = Dispatcher()


@dp.message(Command('start'))
async def command_handler(message: types.Message):
  ''' handle bot /start command
  '''
  await message.answer('Привет! Как поживаешь?')


@dp.message()
async def text_handler(message: types.Message):
  ''' handle chat text message
  huggingface.co model backend request '''
  # user message json payload, lead slash remove
  json_data = {
    "inputs": message.text
  }
  #await chat_bot.tg_bot_logger.info(
  #  f'json data:{json_data}')

  # huggingface.co model backend request
  async with chat_bot.hf_session.post(url=chat_bot.HF_API_URL,
                                      headers=chat_bot.hf_headers,
                                      json=json_data) as response:
    try:
      assert response.status == 200
      #raise AssertionError('test except clause')
      # log event
      await chat_bot.tg_bot_logger.info(
          f'{chat_bot.hf_model_name} model API request:{response.method} {response.url} {response.status} {response.reason}'
      )
    except AssertionError as error:
      if response.status == 503:
        await message.reply(
            f'Модель не успела загрузиться, попробуй через 5сек:\n{response.status} {response.reason}'
        )
      else:
        await message.reply('Ошибка обработки запроса:\n{} {}'.format(
            response.status, response.reason, response.text))
      # log event
      await chat_bot.tg_bot_logger.error(
          f'{chat_bot.hf_model_name} model API request:{response.method} {response.url} {response.status} {response.reason} {response.text}'
      )
      # raise error
      raise
    response_data = await response.json()
    generated_text = response_data[0]['generated_text']
    # log event
    await chat_bot.tg_bot_logger.info(
        f'{chat_bot.hf_model_name} model API response payload:{generated_text}'
    )
    # try get response payload second line
    if '\n' in generated_text:
      generated_text = generated_text.split('\n')[1][2:]
    await message.reply(generated_text)


async def main():
  ''' init chat bot object
  handle huggingface.co requests (https://docs.aiohttp.org/en/stable/client_reference.html):
    - it is suggested you use a single session for the lifetime of your application to benefit from connection pooling
    - the client session supports the context manager protocol for self closing
  polling bot object events '''
  async with ClientSession() as chat_bot.hf_session:
    chat_bot.hf_model_name = 'Den4ikAI/rugpt3_2ch'
    chat_bot.HF_API_URL = 'https://api-inference.huggingface.co/models/{}'.format(
        chat_bot.hf_model_name)
    chat_bot.hf_headers = {
        'Authorization': 'Bearer {}'.format(environ['HF_TOKEN'])
    }
    chat_bot.tg_bot = Bot(token=environ['CC_TG_TOKEN'])

    await dp.start_polling(chat_bot.tg_bot)


if __name__ == '__main__':
  ''' define chat bot object params
  start tg bot app '''
  chat_bot = modules.chatBot.ChatBot()
  asyncio.run(main())
