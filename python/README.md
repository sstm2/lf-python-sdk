LfApi: a Python SDK
=====

Installation
------------

The latest version of the library can be installed directly from PyPI:

    pip install lfapi

Usage
-----

The Client class is the main interface with the ListenFirst API:

    from lfapi import Client

It requires at minimum a set of client credentials as well as an API key, which
can be loaded from a JSON file:

    c = Client.load(<JSON_FILE_NAME_OR_FILE_OBJECT>)

Once instantiated, the Client object can be used to make customized HTTP
requests to various API endpoints:

    res = c.secure_get('dictionary/datasets')

Commonly used endpoints have dedicated instance methods:

    res = c.list_datasets()
