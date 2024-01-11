import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiohttp import ClientSession
from os import environ
from aiologger.loggers.json import JsonLogger
from logging import INFO, DEBUG
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
  # remove user question string lead slash
  user_text = message.text[1:]
  # huggingface.co model backend request
  async with chat_bot.hf_session.post(url=chat_bot.HF_API_URL,
                                      headers=chat_bot.hf_headers,
                                      json=user_text) as response:
    # log event
    await chat_bot.tg_bot_logger.info(
        '{} model API request:{} {} {} {}'.format(chat_bot.hf_model_name,
                                                  response.method,
                                                  response.url,
                                                  response.status,
                                                  response.reason))
    try:
      response_data = await response.json()
      generated_text = response_data[0]['generated_text']
      # log event
      await chat_bot.tg_bot_logger.info(
          '{} model API response payload:{}'.format(chat_bot.hf_model_name,
                                                    generated_text))
      # try get response payload second line
      if '\n' in generated_text:
        generated_text = generated_text.split('\n')[1][2:]
      await message.reply(generated_text)
    except KeyError:
      await message.reply('Нету ответа, давай еще раз\n{} {}'.format(
          response.status, response.reason))
      # log event
      await chat_bot.tg_bot_logger.error(
          '{} model API payload parsing error:{}'.format(
              chat_bot.hf_model_name, response))
    except asyncio.TimeoutError:
      await message.reply('Таймаут, давай еще раз\n{} {}'.format(
          response.status, response.reason))
      # log event
      await chat_bot.tg_bot_logger.info(
          '{} model API request timeout:{}'.format(chat_bot.hf_model_name,
                                                   response))


async def main():
  ''' init chat bot object
  polling events '''
  # one session for application, handle all huggingface.co requests
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
