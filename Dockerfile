FROM python:3.5.5

WORKDIR /app

ADD . /app

RUN pip install -r requirements.txt .
RUN cp configuration/settings.py .

EXPOSE 8020

CMD ["tas-cli", "server"]