from django.http import JsonResponse
from selectolax.parser import HTMLParser

from core.models import Bot, Tip


def create_bet365_tips(session, request):
    bet = request.POST.get('betstring')
    parser = HTMLParser(request.POST.get('innerHTML'))
    bot = Bot.objects.filter(user=session.user).first()

    if not bot:
        return JsonResponse({'error': 'Nenhum bot associado a esta conta.'})

    if 'class="bss-BetBuilderBetItem' in request.POST.get('innerHTML'):
        title = parser.css_first('.bss-BetBuilderBetItem_FixtureDescription').text().strip()
        message_items = []

        for sentence in parser.css('.bss-BetBuilderParticipant_Sentence'):
            message_items.append('📌 Entrada: ' + sentence.text())

        sum_odds = float(parser.css_first('.bss-BetBuilderBetItem_Odds.bs-OddsLabel').text().strip())
        game = title
        odd = sum_odds
        market = title
        new_message = []

        content = '\n'.join(message_items)

        Tip.objects.create(
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
            content=content
        )

    for normal_bet in parser.css('.bss-NormalBetItem'):
        title = normal_bet.css_first('.bss-NormalBetItem_Details .bss-NormalBetItem_Title').text().strip()
        odd = normal_bet.css_first('.bss-NormalBetItem_Details .bss-NormalBetItem_OddsContainer').text().strip()
        market = normal_bet.css_first('.bss-NormalBetItem_Details .bss-NormalBetItem_MarketContainer').text().strip()
        game = normal_bet.css_first('.bss-NormalBetItem_Details .bss-NormalBetItem_BottomSection').text().strip()
        sum_odds = parser.css_first('.bsc-OddsLabel')

        if sum_odds:
            sum_odds = float(sum_odds.text().strip())

        Tip.objects.create(
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
            sum_odds=sum_odds
        )
