from aiogram import Bot
from aiohttp import ClientSession
from aiologger.loggers.json import JsonLogger
from logging import INFO, DEBUG


class ChatBot:
  ''' chat bot object
  init default values '''

  tg_bot: Bot
  tg_bot_logger: JsonLogger
  hf_model_name: str
  hf_session: ClientSession
  HF_API_URL: str
  hf_headers: dict

  def __init__(self):
    self.tg_bot_logger = JsonLogger.with_default_handlers(
        name='app-logger',
        level=INFO,
        serializer_kwargs={'ensure_ascii': False},
    )
    self.hf_model_name = ''
    self.HF_API_URL = ''
    self.hf_headers = {}
