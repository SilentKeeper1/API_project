from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from models import Base, BirthdayReservation, Product, Order, Event, EventRegistration, OrderItem
from datetime import datetime
from pydantic import BaseModel
from typing import List

SQLALCHEMY_DATABASE_URL = "sqlite:///./trc.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Цей рядок створює всі таблиці в базі даних на основі моделей,
# визначених у файлі `models.py`. Запустити його потрібно лише один раз.
Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Pydantic моделі
class BirthdayReservationCreate(BaseModel):
    first_name: str
    last_name: str
    date: datetime
    guests: int
    hall: str
    special_requests: str | None = None


class ProductCreate(BaseModel):
    name: str
    price: float
    category: str


class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int = 1


class OrderCreate(BaseModel):
    user_name: str
    items: List[OrderItemCreate]


class EventCreate(BaseModel):
    title: str
    date: datetime
    location: str
    price: float = 0.0


class EventRegistrationCreate(BaseModel):
    first_name: str
    last_name: str
    tickets: int = 1


app = FastAPI(title="ТРЦ API")


# Birthday routes
@app.post("/birthday/reserve")
def reserve_birthday(reservation: BirthdayReservationCreate, db: Session = Depends(get_db)):
    date_value = reservation.date
    if date_value.tzinfo is not None:
        date_value = date_value.replace(tzinfo=None)

    new_res = BirthdayReservation(
        first_name=reservation.first_name,
        last_name=reservation.last_name,
        date=date_value,
        guests=reservation.guests,
        hall=reservation.hall,
        special_requests=reservation.special_requests,
    )
    db.add(new_res)
    db.commit()
    db.refresh(new_res)

    return {
        "msg": "Бронювання підтверджено 🎉",
        "reservation": {
            "id": new_res.id,
            "first_name": new_res.first_name,
            "last_name": new_res.last_name,
            "date": new_res.date.isoformat(),
            "guests": new_res.guests,
            "hall": new_res.hall,
            "special_requests": new_res.special_requests,
            "created_at": new_res.created_at.isoformat(),
        }
    }


@app.get("/birthday/list")
def list_birthdays(db: Session = Depends(get_db)):
    return db.query(BirthdayReservation).all()


# Products
@app.post("/products/add")
def add_product(product: ProductCreate, db: Session = Depends(get_db)):
    new_product = Product(**product.dict())
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return {
        "msg": "Продукт додано ✅",
        "product": {
            "id": new_product.id,
            "name": new_product.name,
            "price": new_product.price,
            "category": new_product.category
        }
    }


@app.get("/products", response_model=List[ProductCreate])
def list_products(db: Session = Depends(get_db)):
    return db.query(Product).all()


# Orders
@app.post("/orders/create")
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    new_order = Order(user_name=order.user_name)
    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    for item in order.items:
        order_item = OrderItem(order_id=new_order.id, product_id=item.product_id, quantity=item.quantity)
        db.add(order_item)

    # Commit transaction лише один раз після додавання всіх елементів
    db.commit()

    return {"msg": "Замовлення створено ✅", "order_id": new_order.id}


@app.get("/orders/{order_id}")
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Замовлення не знайдено 😢")
    return {
        "id": order.id,
        "user_name": order.user_name,
        "items": [
            {"product_id": i.product_id, "quantity": i.quantity}
            for i in order.items
        ]
    }


# Events
@app.post("/events/create")
def create_event(event: EventCreate, db: Session = Depends(get_db)):
    new_event = Event(**event.dict())
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    return {
        "msg": "Івент створено 🎶",
        "event": {
            "id": new_event.id,
            "title": new_event.title,
            "date": new_event.date.isoformat(),
            "location": new_event.location,
            "price": new_event.price
        }
    }


@app.get("/events")
def list_events(db: Session = Depends(get_db)):
    return db.query(Event).all()


# Event Registrations
@app.post("/events/{event_id}/register")
def register_event(event_id: int, reg: EventRegistrationCreate, db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Івент не знайдено 😢")

    new_reg = EventRegistration(event_id=event_id, **reg.dict())
    db.add(new_reg)
    db.commit()
    db.refresh(new_reg)
    return {"msg": "Реєстрація успішна ✅", "registration": new_reg}


@app.get("/events/{event_id}/registrations")
def list_event_regs(event_id: int, db: Session = Depends(get_db)):
    return db.query(EventRegistration).filter(EventRegistration.event_id == event_id).all()
