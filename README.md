[![Build Status](https://travis-ci.org/pmatigakis/text-analysis-service.svg?branch=develop)](https://travis-ci.org/pmatigakis/text-analysis-service)
[![codecov](https://codecov.io/gh/pmatigakis/text-analysis-service/branch/develop/graph/badge.svg)](https://codecov.io/gh/pmatigakis/text-analysis-service)

TAS (text analysis service) is the application that is used by the TopicAxis API
to extract information from plain text or html.


# Installation

Download the source code and install the latest stable version using pip.
Text analysis service requires Python 3. It has been tested on Python 3.5
however it should run of other versions of Python 3.

```bash
git clone https://github.com/pmatigakis/text-analysis-service.git
cd text-analysis-service
git fetch --all
git checkout master
pip install -r requirements.txt .
```

You will have to download some NLTK data.

```bash
python -m nltk.downloader "punkt"
python -m nltk.downloader "averaged_perceptron_tagger"
python -m nltk.downloader "maxent_ne_chunker"
python -m nltk.downloader "words"
```

# Configuration

A settings.py file is required in the folder where the text analysis service
server will start. See the example settings file in the configuration folder for
information about what configuration settings are available. Most of the
configuration variables in the example settings file can be modified using
environment variables. Rename configuration/.env.template to configuration/.env
and change what is required.

# Running

Go into the folder where the settings file exists and start the text analysis
service server.

```bash
tas-cli server
```

# Analysing text

For the moment only analysis of html documents is supported. The html analysis
endpoint is available at `http://<HOST>:<PORT>/api/v2/process/html`. To process the
contents of a web page execute a POST request with the following payload.

```json
{
    "url": "http://the-page-url.com",
    "html": "the web page html goes here...",
    "headers": {
        "header-name": "add the headers of the response in this dictionary"
    }
}
```

The response is a json document with the analysis results.
