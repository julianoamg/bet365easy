import asyncio
import os
from tempfile import NamedTemporaryFile

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from telegram import Bot
from telegram.constants import ParseMode

from core.models import Bot as ModelBot, Tip


async def send_message(bot_client, print_file, bot, message):
    await bot_client.send_photo(
        bot.dialog_id,
        photo=open(print_file.name, 'rb'),
        protect_content=True,
        caption=message,
        parse_mode=ParseMode.MARKDOWN
    )

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
    link = request.POST.get('href')
    source = request.POST.get('innerHTML')
    units = float(request.POST.get('units'))
    bot = ModelBot.objects.filter(user=session.user).first()

    message = [f'💰 *Unidades:* {units}']
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
    except IndexError:
        anchor = ''

    message.append(f'https://www.bet365.com/dl/sportsbookredirect?bet=1&bs=' + '|'.join(parts) + anchor)
    message = '\n\n'.join(message)
    bot_client = Bot(bot.token)

    tip = Tip.objects.create(
        user=session.user,
        bot=bot,
        bet=bet,
        units=units,
        link=link,
        house=Tip.House.BET365,
        source=source
    )

    with NamedTemporaryFile(mode='wb', delete=False) as print_file:
        options = Options()
        options.add_argument('--headless=new')
        options.add_argument('--window-size=1920,2000')
        driver = WebDriver(options=options)
        driver.get(f'http://127.0.0.1:8000/tip/{tip.id}/')
        screenshot = driver.find_element(By.CSS_SELECTOR, '.bss-StandardBetslip .bss-StandardBetslip_ContentWrapper').screenshot_as_png
        print_file.write(screenshot)
        driver.quit()

    asyncio.run(send_message(bot_client, print_file, bot, sanitize_message(message)))
