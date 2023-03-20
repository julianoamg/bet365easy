import asyncio
import os
from tempfile import NamedTemporaryFile
from urllib.request import urlopen

from django.http import JsonResponse
from selectolax.parser import HTMLParser
from telegram import Bot
from telegram.constants import ParseMode
from telegram.error import BadRequest

from core.models import Bot as ModelBot, Tip


async def send_message(bot_client, print_file, send_print, bot, message):
    if send_print:
        await bot_client.send_photo(
            bot.dialog_id,
            photo=open(print_file.name, 'rb'),
            protect_content=True,
            caption=message,
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        await bot_client.send_message(
            bot.dialog_id,
            message,
            disable_web_page_preview=True,
            parse_mode=ParseMode.MARKDOWN
        )

    if print_file:
        os.unlink(print_file.name)


def sanitize_message(message):
    message_parts = []
    for part in message.split('\n'):
        message_parts.append(part.strip())
    return '\n'.join(message_parts)


class AttributeDict(dict):
    __slots__ = ()
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__


def create_bet365_tips(session, request):
    bet = request.POST.get('betstring')
    innerHTML = request.POST.get('innerHTML')
    link = request.POST.get('href')
    message = []
    similar_tips = []
    bot = ModelBot.objects.filter(user=session.user).first()
    create_bet = 'class="bss-BetBuilderBetItem' in innerHTML if innerHTML else False
    similar_count = 1

    if innerHTML:
        parser = HTMLParser(innerHTML)
        similar_tips = []

        if not bot:
            return JsonResponse({'error': 'Nenhum bot associado a esta conta.'})

        if 'class="bss-BetBuilderBetItem' in innerHTML:
            title = parser.css_first('.bss-BetBuilderBetItem_FixtureDescription').text().strip()
            message_items = []
            index = 1

            for sentence in parser.css('.bss-BetBuilderParticipant_Sentence'):
                message_items.append(f'📌 *{index}*: ' + sentence.text().replace('Pagamento Antecipado', '').strip())
                index += 1

            sum_odds = float(parser.css_first('.bss-BetBuilderBetItem_Odds.bs-OddsLabel').text().strip())
            game = title
            odd = sum_odds
            market = title

            content = '\n'.join(message_items)

            similar_tips.append(AttributeDict(
                user=session.user,
                bot=bot,
                title=title,
                odd=odd,
                market=market,
                game=game,
                bet=bet,
                link=link,
                units=float(request.POST.get('units')),
                house=Tip.House.BET365,
                sum_odds=sum_odds,
                create_bet=True,
                content=content,
                sent=True
            ))

        for normal_bet in parser.css('.bss-NormalBetItem'):
            title = normal_bet.css_first('.bss-NormalBetItem_Details .bss-NormalBetItem_Title').text().strip()
            odd = normal_bet.css_first('.bss-NormalBetItem_Details .bss-NormalBetItem_OddsContainer').text().strip()
            market = normal_bet.css_first('.bss-NormalBetItem_Details .bss-NormalBetItem_MarketContainer').text().strip()
            game = normal_bet.css_first('.bss-NormalBetItem_Details .bss-NormalBetItem_BottomSection').text().strip()
            sum_odds = parser.css_first('.bsc-OddsLabel')

            if sum_odds:
                sum_odds = float(sum_odds.text().strip())

            similar_tips.append(AttributeDict(
                user=session.user,
                bot=bot,
                title=title,
                odd=odd,
                market=market,
                game=game,
                bet=bet,
                link=link,
                units=float(request.POST.get('units')),
                house=Tip.House.BET365,
                sum_odds=sum_odds,
                create_bet=False,
                sent=True
            ))

        tip = similar_tips[0]
        similar_count = len(similar_tips)

        if create_bet:
            message.append('⚠️ *Criar Aposta* ⚠️')
            message.append('')

        if similar_count > 1:
            message.append('⚠️ *Aposta Múltipla* ⚠️')
            message.append('')

        if not create_bet:
            for similar_tip in similar_tips:
                message.append(f"""
                            🏟️ *Jogo:* {similar_tip.game} 
                            📊 *Mercado:* {similar_tip.market}
                            📌 *Entrada:* {similar_tip.title} @ {similar_tip.odd}
                        """.strip())

                if similar_count > 1:
                    message.append(
                        '----------------------')

        if create_bet:
            message.append(
                '----------------------')
            for line in tip.content.splitlines():
                message.append(line)
            message.append(
                '----------------------')

        if similar_count > 1 or create_bet:
            message.append('')

        message.append(f'🏠 *Casa:* {tip.house}')

        if (similar_count > 1 or create_bet) and tip.sum_odds:
            message.append(f'📌 *Odd:* {tip.sum_odds}')

    message.append(f'💰 *Unidades:* {tip.units}')

    if similar_count > 1 or create_bet:
        message.append('')

    parts = []

    for bet_string in bet.strip('||').split('||'):
        try:
            bs = bet_string.split('TP=BS', 1)[1].split('#', 1)[0].split('x', 1)[0]
            odd = bet_string.split('o=', 1)[1].split('#', 1)[0]
            parts.append(f'{bs}~{odd}')
        except IndexError:
            continue

    try:
        anchor = '#' + link.split('#')[1]
    except (IndexError, AttributeError):
        anchor = ''

    if create_bet:
        message.append(link)
    else:
        message.append(f'https://www.bet365.com/dl/sportsbookredirect?bet=1&bs=' + '|'.join(parts) + anchor)

    message = '\n'.join(message)
    bot_client = Bot(bot.token)

    if not message:
        return

    send_print_file = bool(request.POST.get('print'))
    print_file = None

    if send_print_file:
        with NamedTemporaryFile(mode='wb+', delete=False) as print_file:
            response = urlopen(request.POST.get('print'))
            print_file.write(response.file.read())

    asyncio.run(send_message(bot_client, print_file, send_print_file, bot, sanitize_message(message)))
    add_tips = []

    for similar_tip in similar_tips:
        add_tips.append(Tip(**similar_tip))
    Tip.objects.bulk_create(add_tips)
