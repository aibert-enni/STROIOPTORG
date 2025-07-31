# Project Name: **STROIOPTORG**

### Проект в разработке

## Описание

Этот проект представляет собой **систему онлайн-магазина**, включающую функционал создания товаров, показа каталога товаров с фильтрацией по атрибутам, добавления в корзину даже если пользователь не авторизован, оформления заказов, управления товарами, оплатой и возвратами. Приложение также интегрировано с **Stripe** для обработки платежей.

---
Скриншоты:
<img width="960" height="540" alt="Снимок1" src="https://github.com/user-attachments/assets/c5f6c975-cfb1-4e6f-b61d-5853181680b1" />
<img width="960" height="540" alt="Снимок2" src="https://github.com/user-attachments/assets/6032b7b0-eb18-4153-afc3-990f27711d92" />
<img width="960" height="540" alt="Снимок3" src="https://github.com/user-attachments/assets/46571d53-9ca1-4b48-a874-c5a6c1344f38" />
<img width="960" height="540" alt="Снимок4" src="https://github.com/user-attachments/assets/865dfd3d-5f18-42bd-a0b2-8c2405480d38" />
<img width="960" height="540" alt="Снимок5" src="https://github.com/user-attachments/assets/6afb2afe-3e9b-42f9-84fc-55149fb4bd8c" />
<img width="960" height="540" alt="Снимок6" src="https://github.com/user-attachments/assets/b9d7d890-23b3-486e-8e44-5497095663d3" />
<img width="960" height="540" alt="Снимок7" src="https://github.com/user-attachments/assets/b2eefcdb-6e8a-4d97-89c1-6c54bb7bf775" />
<img width="960" height="540" alt="Снимок10" src="https://github.com/user-attachments/assets/a2ca6dfd-7706-4eb6-ba8f-c05dd0e6fd76" />
<img width="960" height="540" alt="Снимок9" src="https://github.com/user-attachments/assets/5b4bfa4a-062f-474b-8caa-5e3e8e391c50" />
<img width="960" height="540" alt="Снимок11" src="https://github.com/user-attachments/assets/b5e9c4df-5743-46f6-8133-2236813f9e5c" />

---
## Стек технологий

- **Backend**: Django, Django Rest Framework, dj-rest-auth
- **Database**: SQLite
- **Frontend**: HTML, CSS, JavaScript, Tailwind
- **Платёжная система**: Stripe
- **Асинхронные задачи**: Celery, Redis
- **Поисковая система**: Elasticsearch
- **Тестирование**: Pytest/Django Test Framework

---
## Установка

### 1. Клонирование репозитория
```shell
git clone https://github.com/aibert-enni/stroiopstorg.git cd stroioptorg
```
### 2. Установка зависимостей

Убедитесь, что у вас установлен Python 3.10. Рекомендуется использовать виртуальное окружение.

Создайте виртуальное окружение:
```shell
python -m venv venv
```

Активируйте виртуальное окружение:

- **Windows**: `venv\Scripts\activate`
- **Mac/Linux**: `source venv/bin/activate`

Установите зависимости:
```shell
pip install -r requirements.txt
```
### 3. Настройка базы данных

Примените миграции для настройки базы данных:
```shell
python manage.py migrate
```

### 4. Запуск сервера
Поднимаем докер:
```shell
docker compose up
```

В корневой папке где settings(stroioptorg) поднимаем celery:
```shell
celery -A stroioptorg worker --loglevel=info --pool=solo
```

Включаем слушатель stripe:
```shell
stripe listen --forward-to localhost:8000/api/v1/stripe/webhook/
```

При добавлении или удалении товара обновляем elasticsearch
```shell
python manage.py search_index --rebuild
```

Для запуска локального сервера:
```shell
py manage.py runserver
```


Перейдите по адресу [http://127.0.0.1:8000/](http://127.0.0.1:8000/) для доступа к приложению.

### API
Перейдите по адресу [http://127.0.0.1:8000/api/schema/swagger-ui/](http://127.0.0.1:8000/api/schema/swagger-ui/) для доступа к документации API

---

## Функционал
### Авторизация
1. **Регистрация с подтверждением почты**
2. **Сброс пароля с помощью почты**
3. **Вход с помощью авторизации через гугл аккаунт**
4. **JWT токены**
### Товар
1. **Создание товара через админку**
2. **Показ каталога товаров с фильтрацией по атрибутам товара и цене**
3. **Страница товара**
4. **Реализована скидка на товар**(пока только в самой модели товара, в будущем сделаю полноценную систему купонов и скидок)
5. **Поиск товара по имени или атрибутам**
### Избранное
1. **Добавление товара в избранное или удаление с него**
### Корзина
1. **Возможность добавлять, обновлять или удалять товары в корзину товары**(через сессию и авторизацию)
2. **Переход товаров с корзины когда пользователь авторизовался**
### Заказ
1. **Создание заказа**: Пользователи могут оформлять заказы, добавляя товары в корзину и завершив процесс покупки.
2. **Управление товарами**: Система поддерживает инвентаризацию и автоматическое обновление остатков при создании и отмене заказов.
3. **Платёжная система (Stripe)**: Интеграция с Stripe для обработки платежей, поддержка возвратов.
4. **Отмена заказа**: Возможность отмены заказа с возвратом товаров на склад.
5. **Статусы заказов**: Заказы могут быть в статусах "в обработке", "отменён", "завершён".
---

