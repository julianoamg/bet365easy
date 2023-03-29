import asyncio

import telegram
from asgiref.sync import sync_to_async
from django.core.management import BaseCommand
from telegram import Bot as PyBot

from core.models import Bot


@sync_to_async
def save_members_qty(bot, members_qty):
    bot.members_qty = members_qty
    bot.save()


async def count_members(bot):
    pybot = PyBot(bot.token)
    members_qty = await pybot.get_chat_member_count(bot.dialog_id)
    await save_members_qty(bot, members_qty)
    print(f'Updating dialog {bot.dialog_name} with {bot.members_qty} members qty')


class Command(BaseCommand):
    help = ''

    def handle(self, *args, **options):
        for bot in Bot.objects.all():
            try:
                asyncio.run(count_members(bot))
            except telegram.error.BadRequest:
                continue
