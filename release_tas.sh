#!/usr/bin/env bash

set -e

if [ -z $1 ]; then
    echo "Declare which version part will be bumped"
    exit
fi

RELEASE_DIR=$(mktemp -d -t tas-XXXXXXXXXX)
TOOLS_VIRTUALENV=$RELEASE_DIR/virtualenv_tools
TAS_VIRTUALENV=$RELEASE_DIR/virtualenv_tas
REPOSITORY=git@github.com:topicaxis/text-analysis-service.git

cd $RELEASE_DIR

virtualenv --python=python3 $TOOLS_VIRTUALENV
$TOOLS_VIRTUALENV/bin/pip install bumpversion==0.5.3 flake8==3.7.7

virtualenv --python=python3 $TAS_VIRTUALENV

git clone $REPOSITORY
cd text-analysis-service
git fetch --all

git checkout master
git merge develop

$TOOLS_VIRTUALENV/bin/bumpversion --commit --message "Released version {new_version}" --tag --tag-name "v{new_version}" $1

$TOOLS_VIRTUALENV/bin/flake8 tas
$TOOLS_VIRTUALENV/bin/flake8 tests

$TAS_VIRTUALENV/bin/pip install -r requirements.txt .
$TAS_VIRTUALENV/bin/python -m nltk.downloader "punkt"
$TAS_VIRTUALENV/bin/python -m nltk.downloader "averaged_perceptron_tagger"
$TAS_VIRTUALENV/bin/python -m nltk.downloader "maxent_ne_chunker"
$TAS_VIRTUALENV/bin/python -m nltk.downloader "words"
$TAS_VIRTUALENV/bin/python setup.py test

git push origin master --tags

git checkout develop
git merge master
git push origin develop