#Вопрос ИИ#
######################################################
def ai_handler(message):
    # Получение запроса пользователя
    user_query = message.text[4:].strip()

    # Проверка наличия запроса
    if not user_query:
        bot.reply_to(message, 'Произошла ошибка. Введен некорректный вопрос.')
        return

    # Задание параметров для API OpenAI
    model_engine = "text-davinci-003" # модель языковой модели
    max_tokens = 3000 # максимальное количество сгенерированных токенов

    # Генерация ответа от API OpenAI
    response = openai.Completion.create(
        engine=model_engine,
        prompt=user_query,
        max_tokens=max_tokens,
        temperature = 0.1,
    )

    # Отправка ответа пользователю
    answer = response.choices[0].text.strip()
    bot.reply_to(message, answer)
######################################################


#Вопрос ИИ картинка#
######################################################
@bot.message_handler(commands=['dalle'])
def dalle_handler(message):
    # Получение запроса пользователя
    user_query = message.text[7:].strip()

    # Проверка наличия запроса
    if not user_query:
        bot.reply_to(message, 'Введите запрос после команды /dalle')
        return

    # Задание параметров для API DALL-E
    api_key = "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"
    url = "https://api.openai.com/v1/images/generations"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    data = {
        "model": "image-alpha-001",
        "prompt": user_query,
        "num_images": 1,
        "size": "512x512",
        "response_format": "url"
    }

    # Получение ответа от API DALL-E
    response = requests.post(url, headers=headers, json=data)
    if response.status_code != 200:
        bot.reply_to(message, 'Ошибка при запросе к API DALL-E')
        return

    # Получение и отправка изображения пользователю
    image_url = response.json()['data'][0]['url']
    image_response = requests.get(image_url)
    if image_response.status_code != 200:
        bot.reply_to(message, 'Ошибка при получении изображения от API DALL-E')
        return
    image = Image.open(BytesIO(image_response.content))
    image_file = BytesIO()
    image.save(image_file, 'PNG')
    image_file.seek(0)
    bot.send_photo(message.chat.id, photo=image_file)
######################################################