Installation
============

Third party requirements
------------------------

The following applications are required. TAS will probably run with newer
versions of those dependencies.

* Nginx
* tyk gateway v2.3.5
* Consul v0.8.3

Installing using virtualenv
---------------------------
TAS should be installed using virtualenv. Create and activate a python virtual
environment.

.. code-block:: shell

   virtualenv --python=python2.7 virtualenv
   source virtualenv/bin/activate

Download the TAS source code. This example will download the latest
development source code. It is better to use a stable version in production.

.. code-block:: shell

   git clone https://github.com/topicaxis/text-analysis-service.git

Install TAS and it's dependencies.

.. code-block:: shell

   pip install -r requirements.txt
   python setup.py install

.. toctree::
   :maxdepth: 1
