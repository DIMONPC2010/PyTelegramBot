FROM python:3.10

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY ..
RUN pip install --upgrade pip
RUN pip install -r reuirements.txt

CMD telegram_reply.py