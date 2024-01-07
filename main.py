import os
import telebot
import requests
import logging

logger = telebot.logger
telebot.logger.setLevel(logging.INFO)

''' define huggingface.co model parameters
and account token data '''
#hf_model = "ai-forever/rugpt3large_based_on_gpt2"
#hf_model = 'TheBakerCat/2chan_ruGPT3_small'
hf_model = 'Den4ikAI/rugpt3_2ch'
#hf_model = 'BlackSamorez/rudialogpt3_medium_based_on_gpt2_2ch'

logger.info('huggingface.co model: {}'.format(hf_model))

hf_secret = os.environ['HF_TOKEN']

API_URL = "https://api-inference.huggingface.co/models/{}".format(hf_model)
headers = {"Authorization": "Bearer {}".format(hf_secret)
}

''' create new tg bot object
   '''
bot = telebot.TeleBot(os.environ['CC_TG_TOKEN'])

''' command handler - start
   '''
@bot.message_handler(commands=['start', 'help'])
def command_handler(message):
  bot.reply_to(message, 'Привет! Как дела?')

''' text handler
   '''
@bot.message_handler(func=lambda message: True)
def text_handler(message):
  user_text = message.text
  try:
    response = requests.post(API_URL, headers=headers, json=user_text[1:]).json()
    generated_text = response[0]['generated_text']
    if hf_model == 'Den4ikAI/rugpt3_2ch':
      generated_text = generated_text.split('\n')[1][2:]
  except KeyError:
    generated_text = 'Что-то пошло не так. Апишка не ответила.\n - модель не успела загрузиться, попробуй через 10сек\n - токен протух'
    logger.error('API error: {}'.format(response))
  bot.reply_to(message, generated_text)

''' start tg bot app
   '''
bot.polling(non_stop=True, interval=0)
