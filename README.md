
# Проект "Фудграм"
Дипломный проект курса python backend-разработчик - мини-соцсеть с рецептами блюд.
Доступен по IP сервера http://158.160.13.52:8000

# Установка
Склонируйте репозиторий приложения:
git@github.com:DimaLaptev/foodgram-project-react.git

Перейдите в папку проекта:
cd <project-folder>
Установите зависимости для Django:
pip install -r requirements.txt

Установите зависимости для React:
cd frontend
npm install

Создайте базу данных PostgreSQL и настройте соответствующие параметры подключения в файле settings.py в папке backend.
Примените миграции для создания необходимых таблиц базы данных:
python manage.py migrate

Запустите сервер разработки Django:
python manage.py runserver

Запустите сервер разработки React:
cd frontend
npm start

Откройте браузер, проект будет доступен по url-адресу http://localhost:8000

# Автор
Дмитрий Шипилов
P.S. настроен путём долгих проб и ошибок, работа над проектом похожа на строительство башни из палок - одна палка подкосилась и завалился весь дом, внимательней читайте инструкцию
