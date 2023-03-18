import asyncio
import time

from django.core.management import BaseCommand
from telegram import Bot
from telegram.constants import ParseMode
from telegram.error import BadRequest

from core.models import Tip




class Command(BaseCommand):
    help = ''

    def handle(self, **options):
    def handle(self, **options):
