# Телеграм Бот для Технической Поддержки
## Необходимые файлы
![Необходимые файлы]([https://github.com/LoveAHK/telegrambot_market/assets/83274505/af535e98-13b0-4e45-9743-c83e7fbb7031](https://github.com/LoveAHK/telegrambot_market/blob/master/Screenshot_223.png))

## 2.1. Действия для загрузки программы

Для того, чтобы запустить телеграм бота для технической поддержки, нужно скачать файлы проекта с git репозитория.

Ссылка: [github.com/LoveAHK/telegrambot_market](https://github.com/LoveAHK/telegrambot_market)

## 2.2. Действия для запуска программы

Перед запуском приложения необходимо выполнить следующие действия:

1. Установите все необходимые библиотеки, используемые в проекте. Для этого откройте консоль Windows в папке с проектом и выполните команду:<br>
```pip install -r requirements.txt```

2. Выполните действия, описанные в файле **Help.txt**.

3. Запустите файл **sql.py**, чтобы создать базу данных.

4. Отредактируйте файл **config.py** и вставьте следующие значения в соответствующие поля:
- `TOKEN`: токен бота
- `PAYMENTS_TOKEN`: токен платежной системы
- `ADMIN_ID`: ID администратора бота в Telegram

5. Теперь можно запустить файл **main.py**, перейти в бота и прописать команду `/start`.

**Примечание:** Убедитесь, что у вас установлен Python и pip, прежде чем выполнять вышеперечисленные действия.

Приятного использования! 🤖
