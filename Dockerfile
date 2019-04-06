FROM python:3.5.5

WORKDIR /app

ADD . /app

RUN pip install -r requirements.txt .
RUN cp configuration/settings.py .
RUN python -m nltk.downloader "punkt"
RUN python -m nltk.downloader "averaged_perceptron_tagger"
RUN python -m nltk.downloader "maxent_ne_chunker"
RUN python -m nltk.downloader "words"

EXPOSE 8020

CMD ["tas-cli", "server"]