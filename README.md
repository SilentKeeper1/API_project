# 🎉 TRC API (FastAPI + Alembic)

Маленький жартівливий бекенд для торгово-розважального центру.  
Можна:
- 🎂 бронювати святкування ДР
- 🍕 замовляти продукти
- 🛒 створювати замовлення
- 🎤 створювати івенти
- 🎟 реєструватися на івенти

---

## 📂 Структура проекту

project/
├── .venv/                  # Віртуальне середовище Python (не включати у Git)
├── app/
│   ├── api/                # Роути FastAPI
│   │   └── routes.py
│   ├── models/             # SQLAlchemy моделі
│   │   └── user.py
│   ├── db/                 # Підключення до бази даних
│   │   └── session.py
│   ├── core/               # Конфігурації та налаштування
│   │   └── config.py
│   └── main.py             # Точка входу FastAPI
├── alembic/
│   ├── versions/           # Історія міграцій
│   └── env.py              # Налаштування Alembic
├── alembic.ini             # Конфігураційний файл Alembic
├── requirements.txt        # Залежності Python
├── README.md               # Документація проєкту
└── trc.db                  # SQLite база даних
---

## 🛠 Таблиці в БД

### 1. `birthday_reservations`
| Поле | Тип | Опис |
|------|-----|------|
| id | int | PK |
| first_name | str | Ім’я |
| last_name | str | Прізвище |
| date | datetime | Дата святкування |
| guests | int | Кількість гостей |
| hall | str | Зал (за замовчуванням "Main Hall") |
| special_requests | str | Особливі побажання |
| created_at | datetime | Дата створення |

### 2. `products`
| Поле | Тип | Опис |
|------|-----|------|
| id | int | PK |
| name | str | Назва продукту |
| price | float | Ціна |
| category | str | Категорія продукту |

### 3. `orders`
| Поле | Тип | Опис |
|------|-----|------|
| id | int | PK |
| user_name | str | Ім’я користувача |
| date | datetime | Дата замовлення |
| status | str | Статус (pending за замовчуванням) |

### 4. `order_items`
| Поле | Тип | Опис |
|------|-----|------|
| id | int | PK |
| order_id | int | FK на orders |
| product_id | int | FK на products |
| quantity | int | Кількість продукту |

### 5. `events`
| Поле | Тип | Опис |
|------|-----|------|
| id | int | PK |
| title | str | Назва івенту |
| date | datetime | Дата проведення |
| location | str | Місце проведення |
| price | float | Ціна квитка |

### 6. `event_registrations`
| Поле | Тип | Опис |
|------|-----|------|
| id | int | PK |
| event_id | int | FK на events |
| first_name | str | Ім’я учасника |
| last_name | str | Прізвище учасника |
| tickets | int | Кількість квитків |

---

## 🚀 Ендпоїнти

### 🎂 Birthday
- `POST /birthday/reserve` — створити бронювання
- `GET /birthday/list` — список бронювань

### 🍕 Products
- `POST /products/add` — додати продукт
- `GET /products` — список продуктів

### 🛒 Orders
- `POST /orders/create` — створити замовлення
- `GET /orders/{order_id}` — перегляд замовлення

### 🎤 Events
- `POST /events/create` — створити івент
- `GET /events` — список івентів

### 🎟 Event Registrations
- `POST /events/{event_id}/register` — реєстрація на івент
- `GET /events/{event_id}/registrations` — список реєстрацій

---

## ⚡ Запуск проекту

1. Встановити залежності:
```bash
pip install -r requirements.txt
uvicorn main:app --reload