import asyncio

from django.http import JsonResponse
from selectolax.parser import HTMLParser
from telegram import Bot
from telegram.constants import ParseMode
from telegram.error import BadRequest

from core.models import Bot as ModelBot, Tip


async def send_message(bot_client, bot, message):
    await bot_client.send_message(bot.dialog_id, message, disable_web_page_preview=True, parse_mode=ParseMode.MARKDOWN)


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
    parser = HTMLParser(request.POST.get('innerHTML'))
    bot = ModelBot.objects.filter(user=session.user).first()
    similar_tips = []

    if not bot:
        return JsonResponse({'error': 'Nenhum bot associado a esta conta.'})

    if 'class="bss-BetBuilderBetItem' in request.POST.get('innerHTML'):
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
            link=request.POST.get('href'),
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
            link=request.POST.get('href'),
            units=float(request.POST.get('units')),
            house=Tip.House.BET365,
            sum_odds=sum_odds,
            create_bet=False,
            sent=True
        ))

    message = []
    tip = similar_tips[0]
    similar_count = len(similar_tips)

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
                message.append(
                    '---------------------------------------------------------------------------------------')

    if tip.create_bet:
        message.append(
            '---------------------------------------------------------------------------------------')
        for line in tip.content.splitlines():
            message.append(line)
        message.append(
            '---------------------------------------------------------------------------------------')

    if similar_count > 1 or tip.create_bet:
        message.append('')

    message.append(f'🏠 *Casa:* {tip.house}')

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

    bot_client = Bot(tip.bot.token)

    if not message:
        return

    try:
        asyncio.run(send_message(bot_client, bot, sanitize_message(message)))
    except BadRequest:
        print('Bad request')
        return

    add_tips = []
    for similar_tip in similar_tips:
        add_tips.append(Tip(**similar_tip))
    Tip.objects.bulk_create(add_tips)
