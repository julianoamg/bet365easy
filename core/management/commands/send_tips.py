import asyncio
import time

from django.core.management import BaseCommand
from telegram import Bot
from telegram.error import BadRequest

from core.models import Tip


async def send_message(bot, tip, message):
    await bot.send_message(tip.bot.dialog_id, message, disable_web_page_preview=True)


class Command(BaseCommand):
    help = ''

    def handle(self, **options):
        while True:
            time.sleep(1)
            tips = Tip.objects.filter(sent=False)

            for tip in tips:
                try:
                    bs = tip.bet.split('TP=BS', 1)[1].split('#', 1)[0].split('x', 0)[0]
                    odd = tip.bet.split('o=', 1)[1].split('#', 1)[0]
                except IndexError:
                    tip.delete()
                    continue

                link = f'https://www.bet365.com/dl/sportsbookredirect?bet=1&bs={bs}~{odd}'
                message = f"""🏟️ Jogo: {tip.game} 
📊 Mercado: {tip.market}
📌 Entrada: {tip.title} @ {tip.odd}
💰 Unidades: {tip.units}
{link}"""

                bot = Bot(tip.bot.token)

                try:
                    asyncio.run(send_message(bot, tip, message))
                except BadRequest:
                    print('Bad request')
                    continue

                tip.sent = True
                tip.save()
