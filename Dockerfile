FROM python:3.9

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /var/www/clnass505

COPY requirements.txt /var/www/clnass505

RUN pip install --upgrade pip
RUN pip install -r requirements.txt