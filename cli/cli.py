from threading import current_thread
current_thread().name = 'Handler'
import os
import json
from utils.encryption import create_encrypted_config, load_encrypted_config
from datetime import datetime
from functools import wraps
from signal import signal, SIGINT
import stdiomask
import concurrent.futures

try:
    import click
except ModuleNotFoundError:
    print(
        "You should try running pipenv shell and pipenv install per the install instructions"
    )
    print("Or you should only use Python 3.8.X per the instructions.")
    print("If you are attempting to run multiple bots, this is not supported.")
    print("You are on your own to figure this out.")
    exit(0)
import time

from notifications.notifications import NotificationHandler, TIME_FORMAT
from stores.amazon import Amazon
from stores.bestbuy import BestBuyHandler
from utils.logger import log
from utils.version import check_version

from hidebots import hidebots
from killdupes import killdupes

notification_handler = NotificationHandler()
CREDENTIAL_FILE = "config/amazon_credentials.json"

try:
    check_version()
except Exception as e:
    log.error(e)


def handler(signal, frame):
    log.info("Caught the stop, exiting.")
    exit(0)


def notify_on_crash(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except KeyboardInterrupt:
            pass
        except:
            notification_handler.send_notification(f"FairGame has crashed.")
            raise

    return decorator

def await_credential_input():
    username = input("Amazon login ID: ")
    password = stdiomask.getpass(prompt="Amazon Password: ")
    return {
        "username": username,
        "password": password,
    }

@click.group()
def main():
    pass


# @click.command()
# @click.option(
#     "--gpu",
#     type=click.Choice(GPU_DISPLAY_NAMES, case_sensitive=False),
#     prompt="What GPU are you after?",
#     cls=QuestionaryOption,
# )
# @click.option(
#     "--locale",
#     type=click.Choice(CURRENCY_LOCALE_MAP.keys(), case_sensitive=False),
#     prompt="What locale shall we use?",
#     cls=QuestionaryOption,
# )
# @click.option("--test", is_flag=True)
# @click.option("--interval", type=int, default=5)
# @notify_on_crash
# def nvidia(gpu, locale, test, interval):
#     nv = NvidiaBuyer(
#         gpu,
#         notification_handler=notification_handler,
#         locale=locale,
#         test=test,
#         interval=interval,
#     )
#     nv.run_items()


@click.command()
@click.option("--no-image", is_flag=True, help="Do not load images")
@click.option("--headless", is_flag=True, help="Unsupported headless mode. GLHF")
@click.option(
    "--test",
    is_flag=True,
    help="Run the checkout flow, but do not actually purchase the item[s]",
)
@click.option(
    "--delay", type=float, default=3.0, help="Time to wait between checks for item[s]"
)
@click.option(
    "--checkshipping",
    is_flag=True,
    help="Factor shipping costs into reserve price and look for items with a shipping price",
)
@click.option(
    "--detailed",
    is_flag=True,
    help="Take more screenshots. !!!!!! This could cause you to miss checkouts !!!!!!",
)
@click.option(
    "--used",
    is_flag=True,
    help="Show used items in search listings.",
)
@click.option("--single-shot", is_flag=True, help="Quit after 1 successful purchase")
@click.option(
    "--no-screenshots",
    is_flag=True,
    help="Take NO screenshots, do not bother asking for help if you use this... Screenshots are the best tool we have for troubleshooting",
)
@click.option(
    "--disable-presence",
    is_flag=True,
    help="Disable Discord Rich Presence functionallity",
)
@click.option(
    "--disable-sound",
    is_flag=True,
    default=False,
    help="Disable local sounds.  Does not affect Apprise notification " "sounds.",
)
@click.option(
    "--slow-mode",
    is_flag=True,
    default=False,
    help="Uses normal page load strategy for selenium. Default is none",
)
@click.option(
    "--p",
    type=str,
    default=None,
    help="Pass in encryption file password as argument",
)
@click.option(
    "--log-stock-check",
    is_flag=True,
    default=False,
    help="writes stock check information to terminal and log",
)
@click.option(
    "--shipping-bypass",
    is_flag=True,
    default=False,
    help="Will attempt to click ship to address button. USE AT YOUR OWN RISK!",
)
@click.option(
    "--configpath",
    default="config/amazon_config.json",
    help="Can be set to change the path to your config file",
)
@notify_on_crash
def amazon(
    no_image,
    headless,
    test,
    delay,
    checkshipping,
    detailed,
    used,
    single_shot,
    no_screenshots,
    disable_presence,
    disable_sound,
    slow_mode,
    p,
    log_stock_check,
    shipping_bypass,
    configpath

):

    if not os.path.exists("screenshots"):
        try:
            os.makedirs("screenshots")
        except:
            raise

    if not os.path.exists("html_saves"):
        try:
            os.makedirs("html_saves")
        except:
            raise
    if os.path.exists(CREDENTIAL_FILE):
        credential = load_encrypted_config(CREDENTIAL_FILE, p)
        username = credential["username"]
        password = credential["password"]
    else:
        log.info("No credential file found, let's make one")
        log.info("NOTE: DO NOT SAVE YOUR CREDENTIALS IN CHROME, CLICK NEVER!")
        credential = await_credential_input()
        create_encrypted_config(credential, CREDENTIAL_FILE)
        username = credential["username"]
        amazon.password = credential["password"]
    asin_list = []
    reserve_min = []
    reserve_max = []
    if os.path.exists(configpath):
        with open(configpath) as json_file:
            try:
                config = json.load(json_file)
                asin_groups = int(config["asin_groups"])
                amazon_website = config.get(
                    "amazon_website", "smile.amazon.com"
                )
                for x in range(asin_groups):
                    asin_list.append(config[f"asin_list_{x + 1}"])
                    reserve_min.append(float(config[f"reserve_min_1"]))
                    reserve_max.append(float(config[f"reserve_max_1"]))
                # assert isinstance(self.asin_list, list)
            except Exception as e:
                log.error(f"{e} is missing")
                log.error(
                    "amazon_config.json file not formatted properly: https://github.com/Hari-Nagarajan/fairgame/wiki/Usage#json-configuration"
                )
                exit(0)
    else:
        log.error(
            "No config file found, see here on how to fix this: https://github.com/Hari-Nagarajan/fairgame/wiki/Usage#json-configuration"
        )
        exit(0)
    notification_handler.sound_enabled = not disable_sound
    if not notification_handler.sound_enabled:
        log.info("Local sounds have been disabled.")

    amzn_obj = Amazon(
        headless=headless,
        notification_handler=notification_handler,
        checkshipping=checkshipping,
        detailed=detailed,
        used=used,
        single_shot=single_shot,
        no_screenshots=no_screenshots,
        disable_presence=disable_presence,
        slow_mode=slow_mode,
        no_image=no_image,
        log_stock_check=log_stock_check,
        shipping_bypass=shipping_bypass,
        configpath=configpath,
        test=test,
        delay=delay,
        reserve_min=reserve_min,
        reserve_max=reserve_max,
        amazon_website=amazon_website,
        username=username,
        password=password
    )

    # Create necessary sub-directories if they don't exist

    killdupes()
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
            for asin in asin_list[0]:
                executor.submit(amzn_obj.run, asin)
            hidebots()

    except RuntimeError:
        del amzn_obj
        log.error("Exiting Program...")
        time.sleep(5)


@click.command()
@click.option("--sku", type=str, required=True)
@click.option("--headless", is_flag=True)
@notify_on_crash
def bestbuy(sku, headless):
    bb = BestBuyHandler(
        sku, notification_handler=notification_handler, headless=headless
    )
    bb.run_item()


@click.option(
    "--disable-sound",
    is_flag=True,
    default=False,
    help="Disable local sounds.  Does not affect Apprise notification " "sounds.",
)
@click.command()
def test_notifications(disable_sound):
    enabled_handlers = ", ".join(notification_handler.enabled_handlers)
    message_time = datetime.now().strftime(TIME_FORMAT)
    notification_handler.send_notification(
        f"Beep boop. This is a test notification from FairGame. Sent {message_time}."
    )
    log.info(f"A notification was sent to the following handlers: {enabled_handlers}")
    if not disable_sound:
        log.info("Testing notification sound...")
        notification_handler.play_notify_sound()
        time.sleep(2)  # Prevent audio overlap
        log.info("Testing alert sound...")
        notification_handler.play_alarm_sound()
        time.sleep(2)  # Prevent audio overlap
        log.info("Testing purchase sound...")
        notification_handler.play_purchase_sound()
    else:
        log.info("Local sounds disabled for this test.")

    # Give the notifications a chance to get out before we quit
    time.sleep(5)


signal(SIGINT, handler)

main.add_command(amazon)
main.add_command(bestbuy)
main.add_command(test_notifications)
