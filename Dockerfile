FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000 8001

RUN python manage.py collectstatic --noinput

CMD ["gunicorn", "mycity.wsgi:application", "--bind", "0.0.0.0:8000"]

CMD ["gunicorn", "mycity.wsgi:application", "--bind", "0.0.0.0:8000", "--log-level", "debug", "--timeout", "120"]
