from main import get_all_items, types, bot
import core
import random
import string
import time
from datetime import datetime


def get_date():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def generate_receipt_number():
    length = 8
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.choice(letters_and_digits) for _ in range(length))


def get_backup(message):

    backup_filename = core.backup_database()

    with open(backup_filename, 'rb') as f:
        bot.send_document(message.chat.id, f)
