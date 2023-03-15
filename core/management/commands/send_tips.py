import asyncio
import time

from django.core.management import BaseCommand
from telegram import Bot
from telegram.constants import ParseMode
from telegram.error import BadRequest

from core.models import Tip


async def send_message(bot, tip, message):
    await bot.send_message(tip.bot.dialog_id, message, disable_web_page_preview=True, parse_mode=ParseMode.MARKDOWN)


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
            cached_bet_strings = []

            for tip in tips:
                if tip.bet in cached_bet_strings:
                    tip.sent = True
                    tip.save()
                    continue

                cached_bet_strings.append(tip.bet)

                message = []
                similar_tips = Tip.objects.filter(bet=tip.bet, sent=False)
                similar_count = similar_tips.count()

                if tip.create_bet:
                    message.append('⚠️ *Criar Aposta* ⚠️')
                    message.append('')

                if similar_count > 1:
                    message.append('⚠️ *Aposta Múltipla* ⚠️')
                    message.append('')

                if not tip.create_bet:
                    for similar_tip in similar_tips:
                        message.append(f"""
                            🏟️ *Jogo:* {similar_tip.game} 
                            📊 *Mercado:* {similar_tip.market}
                            📌 *Entrada:* {similar_tip.title} @ {similar_tip.odd}
                        """.strip())

                        if similar_count > 1:
                            message.append('---------------------------------------------------------------------------------------')

                if tip.create_bet:
                    message.append(
                        '---------------------------------------------------------------------------------------')
                    for line in tip.content.splitlines():
                        message.append(line)
                    message.append(
                        '---------------------------------------------------------------------------------------')

                if similar_count > 1 or tip.create_bet:
                    message.append('')

                message.append(f'🏠 *Casa:* {tip.get_house_display()}')

                if (similar_count > 1 or tip.create_bet) and tip.sum_odds:
                    message.append(f'📌 *Odd:* {tip.sum_odds}')

                message.append(f'💰 *Unidades:* {tip.units}')

                if similar_count > 1 or tip.create_bet:
                    message.append('')

                if tip.house == Tip.House.BET365:
                    parts = []

                    for bet_string in tip.bet.strip('||').split('||'):
                        try:
                            bs = bet_string.split('TP=BS', 1)[1].split('#', 1)[0].split('x', 1)[0]
                            odd = bet_string.split('o=', 1)[1].split('#', 1)[0]
                            parts.append(f'{bs}~{odd}')
                        except IndexError:
                            continue

                    try:
                        anchor = '#' + tip.link.split('#')[1]
                    except (IndexError, AttributeError):
                        anchor = ''

                    if tip.create_bet:
                        message.append(tip.link)
                    else:
                        message.append(f'https://www.bet365.com/dl/sportsbookredirect?bet=1&bs=' + '|'.join(parts) + anchor)

                if tip.house == Tip.House.BETANO:
                    message.append(tip.link)

                message = '\n'.join(message)

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
