import config
import core
import telebot
from telebot import types
import markup
import sys
from telebot import apihelper
import requests
from io import BytesIO
from PIL import Image
import pymysql
from core import get_all_items
import market_admin


bot = telebot.TeleBot(config.TOKEN, skip_pending=True)

def delete_category(message):
    # Connect to the database
    con = pymysql.connect(host=config.MySQL[0], user=config.MySQL[1], passwd=config.MySQL[2], db=config.MySQL[3])
    cur = con.cursor()

    # Get all categories from the database
    cur.execute("SELECT id, name FROM categories")
    categories = cur.fetchall()

    # Create a keyboard with buttons for each category
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    for category in categories:
        callback_data = f"delete_category_id={category[0]}"
        button = types.InlineKeyboardButton(text=category[1], callback_data=callback_data)
        keyboard.add(button)

    # Send a message with the list of categories and buttons
    bot.send_message(chat_id=message.chat.id, text="Выберите категорию, которую нужно удалить:", reply_markup=keyboard)

    # Close the connection to the database
    cur.close()
    con.close()

@bot.callback_query_handler(func=lambda call: "delete_category_id" in call.data)
def delete_category_confirmation(call):
    category_id = int(call.data.split("=")[1])

    # Connect to the database
    con = pymysql.connect(host=config.MySQL[0], user=config.MySQL[1], passwd=config.MySQL[2], db=config.MySQL[3])
    cur = con.cursor()

    # Delete the category and all products in it
    cur.execute(f"DELETE FROM market WHERE category_id={category_id}")
    cur.execute(f"DELETE FROM categories WHERE id={category_id}")
    
    con.commit()

    # Get updated list of categories
    categories = core.get_categories()

    # Create a new keyboard with updated categories
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    for category in categories:
        callback_data = f"delete_category_id={category[0]}"
        button = types.InlineKeyboardButton(text=category[1], callback_data=callback_data)
        keyboard.add(button)

    # Edit the message with updated keyboard
    bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=keyboard)

    # Close the connection to the database
    cur.close()
    con.close()
def delete_product(message):
    # Connect to the database
    con = pymysql.connect(host=config.MySQL[0], user=config.MySQL[1], passwd=config.MySQL[2], db=config.MySQL[3])
    cur = con.cursor()

    # Select all categories
    cur.execute("SELECT id, name FROM categories")
    categories = cur.fetchall()

    # Create a message with categories
    categories_message = "Выберите категорию, из которой нужно удалить товар:"
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    for category in categories:
        callback_data = f"category_id={category[0]}"
        button = types.InlineKeyboardButton(text=category[1], callback_data=callback_data)
        keyboard.add(button)
    bot.send_message(chat_id=message.chat.id, text=categories_message, reply_markup=keyboard)

    # Close the connection to the database
    cur.close()
    con.close()

@bot.callback_query_handler(func=lambda call: "category_id" in call.data)
def category_selection(call):
    category_id = int(call.data.split("=")[1])
    con = pymysql.connect(host=config.MySQL[0], user=config.MySQL[1], passwd=config.MySQL[2], db=config.MySQL[3])
    cur = con.cursor()
    cur.execute(f"SELECT id, name_tovar FROM market WHERE category_id={category_id}")
    products = cur.fetchall()
    if not products:
        bot.answer_callback_query(callback_query_id=call.id, text="В этой категории нет товаров.")
        return
    products_message = "Выберите товар, который нужно удалить:"
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    for product in products:
        callback_data = f"delete_product_id={product[0]}"
        button = types.InlineKeyboardButton(text=product[1], callback_data=callback_data)
        keyboard.add(button)
    back_callback_data = f"back_to_categories_delete_tovar"
    back_button = types.InlineKeyboardButton(text="Назад", callback_data=back_callback_data)
    keyboard.add(back_button)
    bot.send_message(chat_id=call.message.chat.id, text=products_message, reply_markup=keyboard)
    cur.close()
    con.close()
@bot.callback_query_handler(func=lambda call: "back_to_categories_delete_tovar" in call.data)
def back_to_categories(call):
    categories = core.get_categories()
    categories_message = "Выберите категорию:"
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    for category in categories:
        callback_data = f"category_id={category[0]}"
        button = types.InlineKeyboardButton(text=category[1], callback_data=callback_data)
        keyboard.add(button)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=categories_message, reply_markup=keyboard)

# Обработчик для удаления товара
@bot.callback_query_handler(func=lambda call: "delete_product_id" in call.data)
def delete_product_confirm(call):
    # Extract product ID from callback data
    product_id = int(call.data.split("=")[1])

    # Connect to the database
    con = pymysql.connect(host=config.MySQL[0], user=config.MySQL[1], passwd=config.MySQL[2], db=config.MySQL[3])
    cur = con.cursor()

    # Delete product from the database
    cur.execute(f"DELETE FROM market WHERE id={product_id}")
    con.commit()

    # Send confirmation message
    bot.answer_callback_query(callback_query_id=call.id, text="Товар удален")

    # Close the connection to the database
    cur.close()
    con.close()


def view_products(message):
    con = pymysql.connect(host=config.MySQL[0], user=config.MySQL[1], passwd=config.MySQL[2], db=config.MySQL[3])
    cur = con.cursor()

    # Get categories
    cur.execute("SELECT id, name FROM categories")
    categories = cur.fetchall()
    messagetext1 = f"""
        <b>🗃 Выберите Категорию:</b>
➖➖➖➖➖➖➖➖➖➖
    """
    if categories:
        # Create inline keyboard with categories
        keyboard = telebot.types.InlineKeyboardMarkup()
        for category in categories:
            keyboard.add(telebot.types.InlineKeyboardButton(text=category[1], callback_data=f"category_{category[0]}"))

        # Send message with categories
        bot.send_message(message.chat.id, text=messagetext1, reply_markup=keyboard, parse_mode="HTML")
    else:
        # If there are no categories, send error message
        bot.send_message(message.chat.id, "К сожалению, нет категорий для отображения.")

    cur.close()
    con.close()


# Callback function for category selection
@bot.callback_query_handler(func=lambda call: call.data.startswith("category_"))
def view_category_products(call):
    con = pymysql.connect(host=config.MySQL[0], user=config.MySQL[1], passwd=config.MySQL[2], db=config.MySQL[3])
    cur = con.cursor()

    # Get category id from callback data
    category_id = int(call.data.split("_")[1])

    # Get products in selected category
    cur.execute("SELECT id, name_tovar, price, kolvo, file_id, file_name, type FROM market WHERE category_id=%s", category_id)
    products = cur.fetchall()
    messagetext = f"""
    <b>🎁 Выберите товар:</b>
➖➖➖➖➖➖➖➖➖➖
    """
    if products:
        # Create inline keyboard with products
        keyboard = telebot.types.InlineKeyboardMarkup()
        for product in products:
            keyboard.add(telebot.types.InlineKeyboardButton(text=product[1], callback_data=f"product_{product[0]}_{category_id}"))

        # Add "Назад" button to return to categories selection
        keyboard.add(telebot.types.InlineKeyboardButton(text="Назад", callback_data="back_to_categories"))

        # Send message with products and store category id in callback data
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=messagetext, reply_markup=keyboard, parse_mode="HTML")
    else:
        # If there are no products in selected category, send error message
        bot.answer_callback_query(callback_query_id=call.id, text="К сожалению, в этой категории нет товаров.")

    cur.close()
    con.close()

@bot.callback_query_handler(func=lambda call: call.data == "back_to_categories")
def back_to_categories(call):
    view_products(call.message)

@bot.callback_query_handler(func=lambda call: call.data.startswith("product_"))
def view_product(call):
    con = pymysql.connect(host=config.MySQL[0], user=config.MySQL[1], passwd=config.MySQL[2], db=config.MySQL[3])
    cur = con.cursor()

    # Get product id and category id from callback data
    product_id, category_id = map(int, call.data.split("_")[1:])

    # Get product information
    cur.execute("""
        SELECT m.name_tovar, m.price, m.kolvo, m.file_id, m.file_name, m.type, m.opisanie, m.photo, c.name
        FROM market m
        JOIN categories c ON m.category_id = c.id
        WHERE m.id = %s
    """, product_id)
    product = cur.fetchone()
    if product:
        # Create message with product information
        message =f"""
        <b>🎁 Информация о товаре:</b>
➖➖➖➖➖➖➖➖➖➖
🏷 Название: <code>{product[0]}</code>
🗃 Категория: <code>{product[8]}</code>
💰 Стоимость: <code>{product[1]}₽</code>
📦 Количество: <code>{product[2]}шт</code>
📃 Описание: <b>{product[6]}</b>
        """
        # message = f"Название товара: {product[0]}\nЦена: {product[1]} руб.\nКоличество на складе: {product[2]}"
        
        # Create inline keyboard with download button and back button
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.add(telebot.types.InlineKeyboardButton(text="Скачать файл", callback_data=f"open_file_{product_id}"))
        chat_id = call.message.chat.id
        # Edit message with product information and inline keyboard
        bot.send_photo(chat_id,  product[7], caption=message, reply_markup=keyboard, parse_mode="HTML")
        # bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=message, reply_markup=keyboard, parse_mode="HTML")

    cur.close()
    con.close()


@bot.callback_query_handler(func=lambda call: call.data.startswith("open_file_"))
def send_file(call):
    con = pymysql.connect(host=config.MySQL[0], user=config.MySQL[1], passwd=config.MySQL[2], db=config.MySQL[3])
    cur = con.cursor()

    # Get product id from callback data
    product_id = int(call.data.split("_")[2])

    # Get file_id from the database
    cur.execute("SELECT file_id, file_name FROM market WHERE id=%s", product_id)
    result = cur.fetchone()

    if result:
        # Send the file to the chat
        bot.send_document(call.message.chat.id, result[0], caption=result[1])

    cur.close()
    con.close()

def add_category(message):
    # Отправляем сообщение пользователю с просьбой ввести название категории
    msg = bot.send_message(message.chat.id, 'Введите название категории')

    # Ожидаем ввода названия категории от пользователя
    bot.register_next_step_handler(msg, process_category_name)

def process_category_name(message):
    # Получаем название категории от пользователя
    category_name = message.text

    # Добавляем категорию в базу данных
    add_category_to_database(category_name)

    # Отправляем сообщение пользователю о том, что категория была успешно добавлена
    bot.send_message(message.chat.id, f'Категория "{category_name}" успешно добавлена')

def add_category_to_database(category_name):
    con = pymysql.connect(host=config.MySQL[0], user=config.MySQL[1], passwd=config.MySQL[2], db=config.MySQL[3])
    cur = con.cursor()

    cur.execute("INSERT INTO categories(name) VALUES(%s)", (category_name,))

    con.commit()

    cur.close()
    con.close()

def add_item(message):
    # Получение всех категорий из базы данных
    categories = core.get_all_categories()
    markups = types.InlineKeyboardMarkup(row_width=1)
    for category in categories:
        button = types.InlineKeyboardButton(text=category[1], callback_data=f"add_item_{category[0]}")
        markups.add(button)
    bot.send_message(chat_id=message.chat.id, text='Выберете категорию', reply_markup=markups)

@bot.callback_query_handler(func=lambda call: call.data.startswith('add_item_'))
def add_item_to_category(call):
    # Получение ID категории
    category_id = int(call.data.split('_')[-1])

    # Формирование сообщения для ввода информации о товаре
    msg = bot.send_message(chat_id=call.message.chat.id, text='Введите название товара')
    bot.register_next_step_handler(msg, lambda message: add_tovar_price(message, category_id))

def add_tovar_price(message, category_id):
    chat_id = message.chat.id
    name_tovar = message.text.strip()
    bot.send_message(chat_id, 'Введите цену товара:')
    bot.register_next_step_handler(message, add_tovar_kolvo, name_tovar, category_id)

def add_tovar_kolvo(message, name_tovar, category_id):
    chat_id = message.chat.id
    try:
        price = float(message.text.strip().replace(',', '.'))
    except ValueError:
        bot.send_message(chat_id, '🚫 Некорректная цена. Попробуйте еще раз.')
        return
    bot.send_message(chat_id, 'Введите количество товара:')
    bot.register_next_step_handler(message, add_tovar_description, name_tovar, price, category_id)

def add_tovar_description(message, name_tovar, price, category_id):
    chat_id = message.chat.id
    kolvo = message.text.strip()
    bot.send_message(chat_id, 'Введите Описание товара:')
    bot.register_next_step_handler(message, add_tovar_photo, name_tovar, price, category_id, kolvo)

def add_tovar_photo(message, name_tovar, price, category_id, kolvo):
    chat_id = message.chat.id
    opisanie = message.text.strip()
    bot.send_message(chat_id, 'Прикрепите фото товара:')
    bot.register_next_step_handler(message, add_tovar_file, name_tovar, price, category_id, kolvo, opisanie)

def add_tovar_file(message, name_tovar, price, category_id, kolvo, opisanie):
    chat_id = message.chat.id
    photo=message.photo[0].file_id
    bot.send_message(chat_id, 'Прикрепите файл товара:')
    bot.register_next_step_handler(message, add_tovar_confirm, name_tovar, price, category_id, kolvo, opisanie, photo)


def add_tovar_confirm(message,  name_tovar, price, category_id, kolvo, opisanie, photo):
    chat_id = message.chat.id
    if message.text is not None and (otmena := message.text.strip()) == 'Отмена':
        bot.send_message(message.chat.id, 'Отменено.', reply_markup=markup.markup_admin())
        return
    if message.document is not None:
        file_id = message.document.file_id
        file_name = message.document.file_name
        file_type = message.document.mime_type
        core.add_file(message.message_id, file_id, file_name, file_type)
        con = pymysql.connect(
            host=config.MySQL[0], user=config.MySQL[1], passwd=config.MySQL[2], db=config.MySQL[3])
        cur = con.cursor()
        cur.execute(
            f"INSERT INTO market (`name_tovar`, `price`, `kolvo`, `file_id`, `file_name`, `type`, `opisanie`, `photo`, `category_id`) VALUES ('{name_tovar}', '{price}', '{kolvo}', '{file_id}', '{file_name}', '{file_type}', '{opisanie}', '{photo}', '{category_id}')")
        con.commit()
        cur.close()
        con.close()
        bot.send_message(
            chat_id, f'✅ Товар {name_tovar} добавлен в базу данных.', reply_markup=markup.markup_tovars_admin())
    else:
        bot.send_message(
            chat_id, '❌ Не удалось получить файл. Попробуйте еще раз.')
        bot.register_next_step_handler(
            message, add_tovar_confirm,  name_tovar, price, category_id, kolvo, opisanie, photo)
    return


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, '👋🏻 Привет! Это бот для технической поддержки пользователей.\nЕсли у тебя есть какой-либо вопрос или проблема - нажми на кнопку <b>Написать запрос</b> и наши сотрудники в скором времени тебе ответят!', parse_mode='html', reply_markup=markup.markup_main())

@bot.message_handler(commands=['agent'])
def agent(message):
    user_id = message.from_user.id

    if core.check_agent_status(user_id) == True: 
        bot.send_message(message.chat.id, '🔑 Вы авторизованы как Агент поддержки', parse_mode='html', reply_markup=markup.markup_agent())

    else:
        take_password_message = bot.send_message(message.chat.id, '⚠️ Тебя нет в базе. Отправь одноразовый пароль доступа.', reply_markup=markup.markup_cancel())

        bot.clear_step_handler_by_chat_id(message.chat.id)
        bot.register_next_step_handler(take_password_message, get_password_message)


@bot.message_handler(commands=['admin'])
def admin(message):
    user_id = message.from_user.id

    if str(user_id) == config.ADMIN_ID:
        bot.send_message(message.chat.id, '🔑 Вы авторизованы как Админ', reply_markup=markup.markup_admin())
    else:
        bot.send_message(message.chat.id, '🚫 Эта команда доступна только администратору.')



@bot.message_handler(content_types=['text'])
def send_text(message):
    user_id = message.from_user.id

    if message.text == '✏️ Написать запрос':
        take_new_request = bot.send_message(message.chat.id, 'Введите свой запрос и наши сотрудники скоро с вами свяжутся.', reply_markup=markup.markup_cancel())

        bot.clear_step_handler_by_chat_id(message.chat.id)
        bot.register_next_step_handler(take_new_request, get_new_request)

    elif message.text == '✉️ Мои запросы':
        markup_and_value = markup.markup_reqs(user_id, 'my_reqs', '1')
        markup_req = markup_and_value[0]
        value = markup_and_value[1]

        if value == 0:
            bot.send_message(message.chat.id, 'У вас пока ещё нет запросов.', reply_markup=markup.markup_main())
        else:
            bot.send_message(message.chat.id, 'Ваши запросы:', reply_markup=markup_req)
    elif message.text == '🎁 Добавить товары':
        add_item(message)
    elif message.text == '🎁 Просмотр товаров':
        view_products(message)
    elif message.text == '🗃 Создать категорию':
        add_category(message)
    elif message.text == '🎁 Удалить товары ⛔️':
        delete_product(message)
    elif message.text == '🗃 Удалить категорию ⛔️':
        delete_category(message)
    elif message.text == '🎁 Изменить товар 🖍':
        delete_category(message)
    elif message.text == '🔙 Главное меню':
        admin(message)
    else:
        bot.send_message(message.chat.id, 'Вы возвращены в главное меню.', parse_mode='html', reply_markup=markup.markup_main())


def get_password_message(message):
    password = message.text
    user_id = message.from_user.id

    if password == None:
        send_message = bot.send_message(message.chat.id, '⚠️ Вы отправляете не текст. Попробуйте еще раз.', reply_markup=markup.markup_cancel())

        bot.clear_step_handler_by_chat_id(message.chat.id)
        bot.register_next_step_handler(send_message, get_password_message)

    elif password.lower() == 'отмена':
        bot.send_message(message.chat.id, 'Отменено.', reply_markup=markup.markup_main())
        return

    elif core.valid_password(password) == True:
        core.delete_password(password)
        core.add_agent(user_id)

        bot.send_message(message.chat.id, '🔑 Вы авторизованы как Агент поддержки', parse_mode='html', reply_markup=markup.markup_main())
        bot.send_message(message.chat.id, 'Выберите раздел технической панели:', parse_mode='html', reply_markup=markup.markup_agent())

    else:
        send_message = bot.send_message(message.chat.id, '⚠️ Неверный пароль. Попробуй ещё раз.', reply_markup=markup.markup_cancel())

        bot.clear_step_handler_by_chat_id(message.chat.id)
        bot.register_next_step_handler(send_message, get_password_message)


def get_agent_id_message(message):
    agent_id = message.text

    if agent_id == None:
        take_agent_id_message = bot.send_message(message.chat.id, '⚠️ Вы отправляете не текст. Попробуйте еще раз.', reply_markup=markup.markup_cancel())

        bot.clear_step_handler_by_chat_id(message.chat.id)
        bot.register_next_step_handler(take_agent_id_message, get_agent_id_message)

    elif agent_id.lower() == 'отмена':
        bot.send_message(message.chat.id, 'Отменено.', reply_markup=markup.markup_main())
        return

    else:
        core.add_agent(agent_id)
        bot.send_message(message.chat.id, '✅ Агент успешно добавлен.', reply_markup=markup.markup_main())
        bot.send_message(message.chat.id, 'Выберите раздел админ панели:', reply_markup=markup.markup_admin())


def get_new_request(message):
    request = message.text
    user_id = message.from_user.id
    check_file = core.get_file(message)

    #Если пользователь отправляет файл
    if check_file != None:
        file_id = check_file['file_id']
        file_name = check_file['file_name']
        type = check_file['type']
        request = check_file['text']

        if str(request) == 'None':
            take_new_request = bot.send_message(message.chat.id, '⚠️ Вы не ввели ваш запрос. Попробуйте ещё раз, отправив текст вместе с файлом.', reply_markup=markup.markup_cancel())

            bot.clear_step_handler_by_chat_id(message.chat.id)
            bot.register_next_step_handler(take_new_request, get_new_request)

        else:
            req_id = core.new_req(user_id, request)
            core.add_file(req_id, file_id, file_name, type)

            bot.send_message(message.chat.id, f'✅ Ваш запрос под ID {req_id} создан. Посмотреть текущие запросы можно нажав кнопку <b>Мои текущие запросы</b>', parse_mode='html', reply_markup=markup.markup_main())        
    
    #Если пользователь отправляет только текст
    else:
        if request == None:
            take_new_request = bot.send_message(message.chat.id, '⚠️ Отправляемый вами тип данных не поддерживается в боте. Попробуйте еще раз отправить ваш запрос, использовав один из доступных типов данных (текст, файлы, фото, видео, аудио, голосовые сообщения)', reply_markup=markup.markup_cancel())

            bot.clear_step_handler_by_chat_id(message.chat.id)
            bot.register_next_step_handler(take_new_request, get_new_request)

        elif request.lower() == 'отмена':
            bot.send_message(message.chat.id, 'Отменено.', reply_markup=markup.markup_main())
            return

        else:
            req_id = core.new_req(user_id, request)
            bot.send_message(message.chat.id, f'✅ Ваш запрос под ID {req_id} создан. Посмотреть текущие запросы можно нажав кнопку <b>Мои текущие запросы</b>', parse_mode='html', reply_markup=markup.markup_main())


def get_additional_message(message, req_id, status):
    additional_message = message.text
    check_file = core.get_file(message)
    
    #Если пользователь отправляет файл
    if check_file != None:
        file_id = check_file['file_id']
        file_name = check_file['file_name']
        type = check_file['type']
        additional_message = check_file['text']

        core.add_file(req_id, file_id, file_name, type)

    if additional_message == None:
        take_additional_message = bot.send_message(chat_id=message.chat.id, text='⚠️ Отправляемый вами тип данных не поддерживается в боте. Попробуйте еще раз отправить ваше сообщение, использовав один из доступных типов данных (текст, файлы, фото, видео, аудио, голосовые сообщения).', reply_markup=markup.markup_cancel())

        bot.clear_step_handler_by_chat_id(message.chat.id)
        bot.register_next_step_handler(take_additional_message, get_additional_message, req_id, status)

    elif additional_message.lower() == 'отмена':
        bot.send_message(message.chat.id, 'Отменено.', reply_markup=markup.markup_main())
        return

    else:
        if additional_message != 'None':
            core.add_message(req_id, additional_message, status)

        if check_file != None:
            if additional_message != 'None':
                text = '✅ Ваш файл и сообщение успешно отправлены!'
            else:
                text = '✅ Ваш файл успешно отправлен!'
        else:
            text = '✅ Ваше сообщение успешно отправлено!'
        
        bot.send_message(message.chat.id, text, reply_markup=markup.markup_main())

        if status == 'agent':
            user_id = core.get_user_id_of_req(req_id)
            try:
                if additional_message == 'None':
                    additional_message = ''

                bot.send_message(user_id, f'⚠️ Получен новый ответ на ваш запрос ID {req_id}!\n\n🧑‍💻 Ответ агента поддержки:\n{additional_message}', reply_markup=markup.markup_main())

                if type == 'photo':
                    bot.send_photo(user_id, photo=file_id, reply_markup=markup.markup_main())
                elif type == 'document':
                    bot.send_document(user_id, document=file_id, reply_markup=markup.markup_main())
                elif type == 'video':
                    bot.send_video(user_id, video=file_id, reply_markup=markup.markup_main())
                elif type == 'audio':
                    bot.send_audio(user_id, audio=file_id, reply_markup=markup.markup_main())
                elif type == 'voice':
                    bot.send_voice(user_id, voice=file_id, reply_markup=markup.markup_main())
                else:
                    bot.send_message(user_id, additional_message, reply_markup=markup.markup_main())
            except:
                pass





@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    user_id = call.message.chat.id

    if call.message:
        if ('my_reqs:' in call.data) or ('waiting_reqs:' in call.data) or ('answered_reqs:' in call.data) or ('confirm_reqs:' in call.data):
            """
            Обработчик кнопок для:

            ✉️ Мои запросы
            ❗️ Ожидают ответа от поддержки,
            ⏳ Ожидают ответа от пользователя
            ✅ Завершенные запросы  
            """

            parts = call.data.split(':')
            callback = parts[0]
            number = parts[1]
            markup_and_value = markup.markup_reqs(user_id, callback, number)
            markup_req = markup_and_value[0]
            value = markup_and_value[1]

            if value == 0:
                bot.send_message(chat_id=call.message.chat.id, text='⚠️ Запросы не обнаружены.', reply_markup=markup.markup_main())
                bot.answer_callback_query(call.id)
                return

            try:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Нажмите на запрос, чтобы посмотреть историю переписки, либо добавить сообщение:', reply_markup=markup_req)
            except:
                bot.send_message(chat_id=call.message.chat.id, text='Ваши запросы:', reply_markup=markup_req)

            bot.answer_callback_query(call.id)

        #Открыть запрос
        elif 'open_req:' in call.data:
            parts = call.data.split(':')
            req_id = parts[1]
            callback = parts[2]

            req_status = core.get_req_status(req_id)
            request_data = core.get_request_data(req_id, callback)
            len_req_data = len(request_data)

            i = 1
            for data in request_data:
                if i == len_req_data:
                    markup_req = markup.markup_request_action(req_id, req_status, callback)
                else:
                    markup_req = None

                bot.send_message(chat_id=call.message.chat.id, text=data, parse_mode='html', reply_markup=markup_req)

                i += 1

            bot.answer_callback_query(call.id)

        #Добавить сообщение в запрос
        elif 'add_message:' in call.data:
            parts = call.data.split(':')
            req_id = parts[1]
            status_user = parts[2]

            take_additional_message = bot.send_message(chat_id=call.message.chat.id, text='Отправьте ваше сообщение, использовав один из доступных типов данных (текст, файлы, фото, видео, аудио, голосовые сообщения)', reply_markup=markup.markup_cancel())

            bot.register_next_step_handler(take_additional_message, get_additional_message, req_id, status_user)

            bot.answer_callback_query(call.id)

        #Завершить запрос
        elif 'confirm_req:' in call.data:
            parts = call.data.split(':')
            confirm_status = parts[1]
            req_id = parts[2]

            if core.get_req_status(req_id) == 'confirm':
                bot.send_message(chat_id=call.message.chat.id, text="⚠️ Этот запрос уже завершен.", reply_markup=markup.markup_main())
                bot.answer_callback_query(call.id)

                return
            
            #Запросить подтверждение завершения
            if confirm_status == 'wait':
                bot.send_message(chat_id=call.message.chat.id, text="Для завершения запроса - нажмите кнопку <b>Подтвердить</b>", parse_mode='html', reply_markup=markup.markup_confirm_req(req_id))
            
            #Подтвердить завершение
            elif confirm_status == 'true':
                core.confirm_req(req_id)
                
                try:
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="✅ Запрос успешно завершён.", reply_markup=markup.markup_main())
                except:
                    bot.send_message(chat_id=call.message.chat.id, text="✅ Запрос успешно завершён.", reply_markup=markup.markup_main())

                bot.answer_callback_query(call.id)

        #Файлы запроса
        elif 'req_files:' in call.data:
            parts = call.data.split(':')
            req_id = parts[1]
            callback = parts[2]
            number = parts[3]

            markup_and_value = markup.markup_files(number, req_id, callback)
            markup_files = markup_and_value[0]
            value = markup_and_value[1]

            if value == 0:
                bot.send_message(chat_id=call.message.chat.id, text='⚠️ Файлы не обнаружены.', reply_markup=markup.markup_main())
                bot.answer_callback_query(call.id)
                return

            try:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Нажмите на файл, чтобы получить его.', reply_markup=markup_files)
            except:
                bot.send_message(chat_id=call.message.chat.id, text='Нажмите на файл, чтобы получить его.', reply_markup=markup_files)

            bot.answer_callback_query(call.id)

        #Отправить файл
        elif 'send_file:' in call.data:
            parts = call.data.split(':')
            id = parts[1]
            type = parts[2]

            file_id = core.get_file_id(id)
            try:
                if type == 'photo':
                    bot.send_photo(call.message.chat.id, photo=file_id, reply_markup=markup.markup_main())
                elif type == 'document':
                    bot.send_document(call.message.chat.id, document=file_id, reply_markup=markup.markup_main())
                elif type == 'video':
                    bot.send_video(call.message.chat.id, video=file_id, reply_markup=markup.markup_main())
                elif type == 'audio':
                    bot.send_audio(call.message.chat.id, audio=file_id, reply_markup=markup.markup_main())
                elif type == 'voice':
                    bot.send_voice(call.message.chat.id, voice=file_id, reply_markup=markup.markup_main())
            
                bot.answer_callback_query(call.id)
            except:
                 bot.send_message(call.message.chat.id, 'Произошла ошибка', parse_mode='html')
        #Вернуться назад в панель агента
        elif call.data == 'back_agent':
            try:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='🔑 Вы авторизованы как Агент поддержки', parse_mode='html', reply_markup=markup.markup_agent())
            except:
                bot.send_message(call.message.chat.id, '🔑 Вы авторизованы как Агент поддержки', parse_mode='html', reply_markup=markup.markup_agent())

            bot.answer_callback_query(call.id)

        #Вернуться назад в панель админа
        elif call.data == 'back_admin':
            try:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='🔑 Вы авторизованы как Админ', parse_mode='html', reply_markup=markup.markup_admin())
            except:
                bot.send_message(call.message.chat.id, '🔑 Вы авторизованы как Админ', parse_mode='html', reply_markup=markup.markup_admin())

            bot.answer_callback_query(call.id)

        #Добавить агента
        elif call.data == 'add_agent':
            take_agent_id_message = bot.send_message(chat_id=call.message.chat.id, text='Чтобы добавить агента поддержки - введите его ID Telegram.', reply_markup=markup.markup_cancel())
            bot.register_next_step_handler(take_agent_id_message, get_agent_id_message)

        #Все агенты
        elif 'all_agents:' in call.data:
            number = call.data.split(':')[1]
            markup_and_value = markup.markup_agents(number)
            markup_agents = markup_and_value[0]
            len_agents = markup_and_value[1]

            if len_agents == 0:
                bot.send_message(chat_id=call.message.chat.id, text='⚠️ Агенты не обнаружены.', reply_markup=markup.markup_main())
                bot.answer_callback_query(call.id)
                return

            try:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Нажмите на агента поддержки, чтобы удалить его', parse_mode='html', reply_markup=markup_agents)
            except:
                bot.send_message(call.message.chat.id, 'Нажмите на агента поддержки, чтобы удалить его', parse_mode='html', reply_markup=markup_agents)

            bot.answer_callback_query(call.id)

        #Удалить агента
        elif 'delete_agent:' in call.data:
            agent_id = call.data.split(':')[1]
            core.delete_agent(agent_id)

            try:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Нажмите на агента поддержки, чтобы удалить его', parse_mode='html', reply_markup=markup.markup_agents('1')[0])
            except:
                bot.send_message(call.message.chat.id, 'Нажмите на агента поддержки, чтобы удалить его', parse_mode='html', reply_markup=markup.markup_agents('1')[0])

            bot.answer_callback_query(call.id)

        #Все пароли
        elif 'all_passwords:' in call.data:
            number = call.data.split(':')[1]
            markup_and_value = markup.markup_passwords(number)
            markup_passwords = markup_and_value[0]
            len_passwords = markup_and_value[1]

            if len_passwords == 0:
                bot.send_message(chat_id=call.message.chat.id, text='⚠️ Пароли не обнаружены.', reply_markup=markup.markup_main())
                bot.answer_callback_query(call.id)
                return

            try:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Нажмите на пароль, чтобы удалить его', parse_mode='html', reply_markup=markup_passwords)
            except:
                bot.send_message(call.message.chat.id, 'Нажмите на пароль, чтобы удалить его', parse_mode='html', reply_markup=markup_passwords)

            bot.answer_callback_query(call.id)

        #Удалить пароль
        elif 'delete_password:' in call.data:
            password = call.data.split(':')[1]
            core.delete_password(password)

            try:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Нажмите на пароль, чтобы удалить его', parse_mode='html', reply_markup=markup.markup_passwords('1')[0])
            except:
                bot.send_message(call.message.chat.id, 'Нажмите на пароль, чтобы удалить его', parse_mode='html', reply_markup=markup.markup_passwords('1')[0])

            bot.answer_callback_query(call.id)

        #Сгенерировать пароли
        elif call.data == 'generate_passwords':
            #10 - количество паролей, 16 - длина пароля
            passwords = core.generate_passwords(10, 16) 
            core.add_passwords(passwords)

            text_passwords = ''
            i = 1
            for password in passwords:
                text_passwords += f'{i}. {password}\n'
                i += 1
            
            bot.send_message(call.message.chat.id, f"✅ Сгенерировано {i-1} паролей:\n\n{text_passwords}", parse_mode='html', reply_markup=markup.markup_main())
            bot.send_message(call.message.chat.id, 'Нажмите на пароль, чтобы удалить его', parse_mode='html', reply_markup=markup.markup_passwords('1')[0])

            bot.answer_callback_query(call.id)

        #Остановить бота
        elif 'stop_bot:' in call.data:
            status = call.data.split(':')[1]

            #Запросить подтверждение на отключение
            if status == 'wait':
                try:
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"Вы точно хотите отключить бота?", parse_mode='html', reply_markup=markup.markup_confirm_stop())
                except:
                    bot.send_message(call.message.chat.id, f"Вы точно хотите отключить бота?", parse_mode='html', reply_markup=markup.markup_confirm_stop())

            #Подтверждение получено
            elif status == 'confirm':
                try:
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='✅ Бот отключен.')
                except:
                    bot.send_message(chat_id=call.message.chat.id, text='✅ Бот отключен.')

                bot.answer_callback_query(call.id)
                bot.stop_polling()
                sys.exit()

        elif call.data.startswith('backtovars'):
            items = get_all_items()
            markups = types.InlineKeyboardMarkup(row_width=1)
            for item in items:
                # Создание кнопки товара
                button = types.InlineKeyboardButton(text=item[1], callback_data=f"view_item_{item[0]}")
                markups.add(button)
            bot.edit_message_text(chat_id=call.message.chat.id, text='Выберете товар', reply_markup=markups, message_id=call.message.id)

        #Callbacks for market_admin
        elif call.data.startswith('give_backup'):
            market_admin.get_backup(call.message)
        elif call.data.startswith('market_admin'):
                bot.send_message(call.message.chat.id, f"Выберете действие", reply_markup=markup.markup_tovars_admin())






if __name__ == "__main__":
    bot.polling(none_stop=True)