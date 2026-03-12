FROM python:3.11-slim

WORKDIR /app

COPY auth_service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY auth_service/ ./auth_service/

ENV DATABASE_URL="sqlite:///./auth_service.db"
ENV SECRET_KEY="Banana"
ENV ALGORITHM="HS256"
ENV ACCESS_TOKEN_EXPIRE_MINUTES="30"

CMD ["uvicorn", "auth_service.main:app", "--host", "0.0.0.0", "--port", "8001"]

