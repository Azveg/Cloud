import os
import telegram
import panda


def talk_bot(request):
    # определяем бота с помощью токена
    bot = telegram.Bot(token=os.environ["TELEGRAM_TOKEN"])
    if request.method == "POST":
        update = telegram.Update.de_json(request.get_json(force=True), bot)
        chat_id = update.message.chat.id
        # Reply with the same message
        bot.sendMessage(chat_id=chat_id, text=panda.answer(str(update.message.text)))
    return "okay"
