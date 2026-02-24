from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse, Response
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError
from app.routers import users, games, trade_offers
from app.database import engine, Base
from app.schemas import ErrorResponse
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
import os
import logging
import time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

INSTANCE_NAME = os.getenv("INSTANCE_NAME", "UNKNOWN")

Base.metadata.create_all(bind=engine)

REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status', 'instance']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint', 'instance']
)

ACTIVE_REQUESTS = Gauge(
    'http_requests_active',
    'Number of active HTTP requests',
    ['instance']
)

app = FastAPI(
    title="Video Game Trading API",
    description="A RESTful API for trading video games with HATEOAS support (REST Level 3)",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    ACTIVE_REQUESTS.labels(instance=INSTANCE_NAME).inc()
    start_time = time.time()

    logger.info(f"[{INSTANCE_NAME}] {request.method} {request.url.path}")
    response = await call_next(request)

    duration = time.time() - start_time

    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code,
        instance=INSTANCE_NAME
    ).inc()

    REQUEST_DURATION.labels(
        method=request.method,
        endpoint=request.url.path,
        instance=INSTANCE_NAME
    ).observe(duration)

    ACTIVE_REQUESTS.labels(instance=INSTANCE_NAME).dec()

    logger.info(f"[{INSTANCE_NAME}] {request.method} {request.url.path} - Status: {response.status_code}")
    response.headers["X-Instance-Name"] = INSTANCE_NAME
    return response


app.include_router(users.router)
app.include_router(games.router)
app.include_router(trade_offers.router)


@app.get("/metrics", tags=["monitoring"])
def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/", tags=["root"])
def root(request: Request):
    base_url = str(request.base_url).rstrip('/')
    return {
        "message": "Video Game Trading API",
        "version": "1.0.0",
        "instance": INSTANCE_NAME,
        "links": {
            "self": {
                "rel": "self",
                "href": f"{base_url}/",
                "method": "GET"
            },
            "register": {
                "rel": "register",
                "href": f"{base_url}/users",
                "method": "POST"
            },
            "users": {
                "rel": "users",
                "href": f"{base_url}/users",
                "method": "GET"
            },
            "games": {
                "rel": "games",
                "href": f"{base_url}/games",
                "method": "GET"
            },
            "trade_offers": {
                "rel": "trade_offers",
                "href": f"{base_url}/trade-offers",
                "method": "GET"
            },
            "documentation": {
                "rel": "documentation",
                "href": f"{base_url}/docs",
                "method": "GET"
            },
            "openapi": {
                "rel": "openapi",
                "href": f"{base_url}/openapi.json",
                "method": "GET"
            }
        }
    }


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        errors.append({
            "field": " -> ".join(str(x) for x in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation Error",
            "detail": "Request validation failed",
            "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY,
            "errors": errors
        }
    )


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Database Error",
            "detail": "An error occurred while processing your request",
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    import traceback
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "detail": str(exc),
            "traceback": traceback.format_exc(),
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR
        }
    )

