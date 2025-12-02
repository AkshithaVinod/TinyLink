# app/crud.py
from sqlalchemy.orm import Session
from .models import URL
from .utils import generate_short_code


def create_short_url(db: Session, original_url: str) -> URL:
    short_code = generate_short_code()
    while db.query(URL).filter(URL.short_code == short_code).first():
        short_code = generate_short_code()  # avoid collision (super rare)
    db_url = URL(short_code=short_code, original_url=original_url)
    db.add(db_url)
    db.commit()
    db.refresh(db_url)
    return db_url


def get_url_by_code(db: Session, short_code: str) -> URL | None:
    return db.query(URL).filter(URL.short_code == short_code).first()


def increment_clicks(db: Session, url: URL):
    url.clicks += 1
    db.commit()