import asyncio
import time

from django.core.management import BaseCommand
from telegram import Bot
from telegram.error import BadRequest

from core.models import Tip


async def send_message(bot, tip, message):
    await bot.send_message(tip.bot.dialog_id, message, disable_web_page_preview=True)


def sanitize_message(message):
    message_parts = []
    for part in message.split('\n'):
        message_parts.append(part.strip())
    return '\n'.join(message_parts)


class Command(BaseCommand):
    help = ''

    def handle(self, **options):
        while True:
            time.sleep(0.5)

            tips = Tip.objects.filter(sent=False)
            message = None
            cached_bet_strings = []

            for tip in tips:
                similar_tips = None

                if tip.bet in cached_bet_strings:
                    tip.sent = True
                    tip.save()
                    continue

                if tip.house == Tip.House.BET365:
                    cached_bet_strings.append(tip.bet)
                    parts = []

                    for bet_string in tip.bet.strip('||').split('||'):
                        try:
                            bs = bet_string.split('TP=BS', 1)[1].split('#', 1)[0].split('x', 1)[0]
                            odd = bet_string.split('o=', 1)[1].split('#', 1)[0]
                            parts.append(f'{bs}~{odd}')
                        except IndexError:
                            continue

                    message = []
                    similar_tips = Tip.objects.filter(bet=tip.bet, sent=False)

                    for similar_tip in similar_tips:
                        message.append(f"""
                            💻️ Casa: {similar_tip.get_house_display()} 
                            🏟️ Jogo: {similar_tip.game} 
                            📊 Mercado: {similar_tip.market}
                            📌 Entrada: {similar_tip.title} @ {tip.odd}
                            💰 Unidades: {similar_tip.units}
                        """.strip())

                    message.append(f'https://www.bet365.com/dl/sportsbookredirect?bet=1&bs=' + '|'.join(parts))
                    message = '\n---------------------------------------------------------------------------------------\n'.join(message)

                if tip.house == Tip.House.BETANO:
                    link = tip.link
                    message = sanitize_message(f"""
                        🕹️️ Casa: {tip.get_house_display()}
                        🏟️ Jogo: {tip.game} 
                        📊 Mercado: {tip.market}
                        📌 Entrada: {tip.title} @ {tip.odd}
                        💰 Unidades: {tip.units}
                        ---------------------------------------------------------------------------------------
                        {link}
                    """)

                bot = Bot(tip.bot.token)

                if message is None:
                    continue

                try:
                    asyncio.run(send_message(bot, tip, sanitize_message(message)))
                except BadRequest:
                    print('Bad request')
                    continue

                tip.sent = True
                tip.save()

                if similar_tips:
                    similar_tips.update(sent=True)
