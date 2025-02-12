# Вибираємо офіційний образ Python
FROM python:3.11

# Встановимо робочу директорію всередині контейнера
WORKDIR /app

# Скопіюємо файли залежностей
COPY pyproject.toml poetry.lock ./

# Встановлюємо Poetry
RUN pip install poetry

# Встановлюємо залежності без створення віртуального середовища
RUN poetry config virtualenvs.create false && poetry install --no-dev --no-interaction --no-ansi

# Скопіюємо код застосунку
COPY . .

# Відкриваємо порт, який буде використовуватись FastAPI
EXPOSE 8000

# Запускаємо FastAPI сервер
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
