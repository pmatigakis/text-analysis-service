FROM python:3.5.5

WORKDIR /app

ADD tas /app/tas
COPY setup.py /app
COPY requirements.txt /app
COPY requirements-test.txt /app
COPY configuration/settings.py /app/configuration/

RUN pip install -r requirements.txt .
RUN python -m nltk.downloader "punkt"
RUN python -m nltk.downloader "averaged_perceptron_tagger"
RUN python -m nltk.downloader "maxent_ne_chunker"
RUN python -m nltk.downloader "words"

EXPOSE 8020

COPY ./docker-entrypoint.sh /app
ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["run"]