from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

from core.crawlers.bet365 import create_bet365_tips
from core.crawlers.betano import create_betano_tips
from core.models import Session, Tip


class IndexView(TemplateView):
    template_name = 'index.html'


class TipView(TemplateView):
    template_name = 'tip.html'

    def get(self, request, identifier):
        tip = Tip.objects.get(id=identifier)
        return render(request, self.template_name, {'tip': tip})


@method_decorator(csrf_exempt, name='dispatch')
class LoginView(View):
    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')
        error_response = {'error': 'Dados inválidos, verifique se os mesmos estão corretos!'}
        user = authenticate(username=email, password=password)
        if user is None:
            return JsonResponse(error_response)
        if user.expire_in_days <= 0:
            return JsonResponse(
                {'error': 'Seu plano expirou, por favor entre em contato com nosso suporte, e faça sua renovação.'})
        Session.objects.filter(user=user).delete()
        session = Session.objects.create(user=user)
        return JsonResponse({'success': True, 'session_id': session.id})


@method_decorator(csrf_exempt, name='dispatch')
class IsAuthenticatedView(View):
    def get(self, request):
        try:
            session = Session.objects.get(id=request.GET.get('session_id'))
            if session.user.expire_in_days <= 0:
                session.delete()
                return JsonResponse({'error': True})
            return JsonResponse({'success': True})
        except (Session.DoesNotExist, ValidationError):
            return JsonResponse({'error': True})


@method_decorator(csrf_exempt, name='dispatch')
class SendTipView(View):
    def post(self, request):
        session = Session.objects.get(id=request.GET.get('session_id'))
        href = request.POST.get('href')
        response = None

        if 'bet365.com' in href:
            response = create_bet365_tips(session, request)
        if 'betano.com' in href:
            response = create_betano_tips(session, request)

        if response:
            return response

        return JsonResponse({'success': True})
