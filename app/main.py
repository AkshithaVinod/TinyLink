from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from .database import SessionLocal, engine, Base
from .models import URL
from .schemas import URLCreate, URLResponse
from .crud import create_short_url, get_url_by_code, increment_clicks
import redis
import os
from prometheus_client import Counter, Histogram, make_asgi_app
import time
from fastapi.responses import RedirectResponse

# Prometheus metrics
REQUEST_COUNT = Counter("http_requests_total", "Total HTTP Requests", ["method", "endpoint", "status"])
REQUEST_LATENCY = Histogram("http_request_duration_seconds", "Request latency", ["endpoint"])

# Redis for rate limiting
redis_client = redis.Redis(host='redis', port=6379, db=0, decode_responses=True)

app = FastAPI(title="TinyLink SRE", description="Production-grade URL shortener")

# Create tables
Base.metadata.create_all(bind=engine)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Rate limiting middleware
@app.middleware("http")
async def rate_limiting_middleware(request: Request, call_next):
    client_ip = request.client.host
    key = f"rate_limit:{client_ip}"
    current = redis_client.incr(key)
    if current == 1:
        redis_client.expire(key, 60)
    if current > 20:  # 20 requests per minute
        REQUEST_COUNT.labels(method=request.method, endpoint=request.url.path, status=429).inc()
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    start_time = time.time()
    response = await call_next(request)
    latency = time.time() - start_time
    REQUEST_LATENCY.labels(endpoint=request.url.path).observe(latency)
    REQUEST_COUNT.labels(method=request.method, endpoint=request.url.path, status=response.status_code).inc()
    return response

# Health checks
@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/ready")
async def ready(db: Session = Depends(get_db)):
    try:
        db.execute("SELECT 1")
        return {"status": "ready"}
    except:
        raise HTTPException(status_code=503, detail="Database not ready")

# Prometheus metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

@app.post("/shorten", response_model=URLResponse, status_code=201)
async def shorten(url: URLCreate, db: Session = Depends(get_db)):
    db_url = create_short_url(db, url.url)
    return URLResponse(
        short_code=db_url.short_code,
        original_url=db_url.original_url,
        clicks=db_url.clicks,
        created_at=db_url.created_at.isoformat()
    )

@app.get("/{short_code}")
async def redirect(short_code: str, db: Session = Depends(get_db)):
    url = get_url_by_code(db, short_code)
    if not url:
        raise HTTPException(status_code=404, detail="Short URL not found")
    increment_clicks(db, url)
    return RedirectResponse(url.original_url, status_code=302)

@app.get("/")
async def root():
    return {"message": "TinyLink SRE - POST /shorten to create, GET /{code} to redirect"}