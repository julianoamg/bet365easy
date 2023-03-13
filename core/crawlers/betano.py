from django.http import JsonResponse
from selectolax.parser import HTMLParser

from core.models import Bot, Tip


def create_betano_tips(session, request):
    parser = HTMLParser(request.POST.get('innerHTML'))
    bot = Bot.objects.filter(user=session.user).first()

    for card in parser.css('.bet-activity-card'):
        market = card.css_first('.market-label').text().strip()
        game = ' x '.join([team.text().strip() for team in card.css('.participants__participant-name')])
        title = card.css_first('.selection-label').text().strip()
        odd = card.css_first('.bet-odds__value').text().strip()
        link = 'https://br.betano.com' + card.css_first('.selection-label').attributes['href']

        if not game.strip():
            game = card.css_first('.event-info').text().strip()

        Tip.objects.create(
            user=session.user,
            bot=bot,
            title=title,
            odd=odd,
            market=market,
            game=game,
            units=float(request.POST.get('units')),
            house=Tip.House.BETANO,
            link=link
        )
