from django.http import JsonResponse
from selectolax.parser import HTMLParser

from core.models import Bot, Tip


def create_bet365_tips(session, request):
    bet = request.POST.get('betstring')
    parser = HTMLParser(request.POST.get('innerHTML'))
    bot = Bot.objects.filter(user=session.user).first()

    if not bot:
        return JsonResponse({'error': 'Nenhum bot associado a esta conta.'})

    for normal_bet in parser.css('.bss-NormalBetItem'):
        title = normal_bet.css_first('.bss-NormalBetItem_Details .bss-NormalBetItem_Title').text()
        odd = normal_bet.css_first('.bss-NormalBetItem_Details .bss-NormalBetItem_OddsContainer').text()
        market = normal_bet.css_first('.bss-NormalBetItem_Details .bss-NormalBetItem_MarketContainer').text()
        game = normal_bet.css_first('.bss-NormalBetItem_Details .bss-NormalBetItem_BottomSection').text()

        Tip.objects.create(
            user=session.user,
            bot=bot,
            title=title.strip(),
            odd=odd.strip(),
            market=market.strip(),
            game=game.strip(),
            bet=bet.strip(),
            units=float(request.POST.get('units')),
            house=Tip.House.BET365
        )
