from main import get_all_items, types, bot
import markup
import core
import pymysql
import config

# def tovars(message):
#     # Получение всех товаров из базы данных
#     items = get_all_items()
#     markups = types.InlineKeyboardMarkup(row_width=1)
#     for item in items:
#         button = types.InlineKeyboardButton(text=item[1], callback_data=f"view_item_{item[0]}")
#         markups.add(button)
#     bot.send_message(chat_id=message.chat.id, text='Выберете товар', reply_markup=markups, reply_to_message_id=message.id)

def get_backup(message):
    # Вызов функции для бэкапа базы данных
    backup_filename = core.backup_database()
    # Отправка файла в чат
    with open(backup_filename, 'rb') as f:
        bot.send_document(message.chat.id, f)

