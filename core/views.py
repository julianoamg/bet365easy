import random
import string

from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from selectolax.parser import HTMLParser

from core.models import Session, Tip, Bot


class IndexView(TemplateView):
    template_name = 'index.html'


@method_decorator(csrf_exempt, name='dispatch')
class LoginView(View):
    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')
        error_response = {'error': 'Dados inválidos, verifique se os mesmos estão corretos!'}

        user = authenticate(username=email, password=password)

        if user is None:
            return JsonResponse(error_response)

        session = Session.objects.create(user=user)
        return JsonResponse({'success': True, 'session_id': session.id})


@method_decorator(csrf_exempt, name='dispatch')
class IsAuthenticatedView(View):
    def get(self, request):
        try:
            Session.objects.get(id=request.GET.get('session_id'))
            return JsonResponse({'success': True})
        except (Session.DoesNotExist, ValidationError):
            return JsonResponse({'error': True})


@method_decorator(csrf_exempt, name='dispatch')
class SendTipView(View):
    def post(self, request):
        try:
            session = Session.objects.get(id=request.GET.get('session_id'))
            bet = request.POST.get('betstring')
            parser = HTMLParser(request.POST.get('innerHTML'))
            title = parser.css_first('.bss-NormalBetItem_Details .bss-NormalBetItem_Title').text()
            odd = parser.css_first('.bss-NormalBetItem_Details .bss-NormalBetItem_OddsContainer').text()
            market = parser.css_first('.bss-NormalBetItem_Details .bss-NormalBetItem_MarketContainer').text()
            game = parser.css_first('.bss-NormalBetItem_Details .bss-NormalBetItem_BottomSection').text()

            Tip.objects.create(
                user=session.user,
                bot=Bot.objects.filter(user=session.user).first(),
                title=title.strip(),
                odd=odd.strip(),
                market=market.strip(),
                game=game.strip(),
                bet=bet.strip(),
                units=float(request.POST.get('units'))
            )
            return JsonResponse({'success': True})
        except (Session.DoesNotExist, ValidationError):
            return JsonResponse({'error': True})
