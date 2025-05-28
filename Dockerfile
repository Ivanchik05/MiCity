FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

RUN python manage.py migrate --noinput
RUN python manage.py collectstatic --noinput

CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "mycity.asgi:application"]