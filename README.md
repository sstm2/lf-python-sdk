
LfApi: a Python SDK
=====

Installation
------------

The latest version of the library can be installed directly from PyPI:

    pip install lfapi

Usage
-----

### Getting Started

The `lfapi.Client` class is the main interface with the ListenFirst API:

    from lfapi import Client

It requires at minimum an API key as well as a set of client credentials for
access token generation. Token generation is handled by the `lfapi.Auth` class:

    from lfapi import Auth
    auth = Auth(<CLIENT_ID>, <CLIENT_SECRET>)
    token = auth.access_token

The `Client` class is instantiated with an API key and an instance of the
`Auth` class:

    c = Client(<API_KEY>, auth)

Alternatively, all three credentials can be loaded directly to the `Client`
class from a JSON file:

    c = Client.load(<JSON_FILE_NAME_OR_FILE_OBJECT>)

    # The JSON file should follow this schema:
    # {
    #   "api_key": <api_key>,
    #   "client_id": <client_id>
    #   "client_secret": <client_secret>
    # }

These credentials can be retrieved from [the platform's API settings page](
https://app.listenfirstmedia.com/#api).

### Accessing the API

Once instantiated, the `Client` object can be used to make customized HTTP
requests to various API endpoints. The lowest-level request mechanism is built
around two methods, `secure_get()` and `secure_post()`. Each takes a positional
endpoint argument, as well as a `params` argument as in the `requests` library.
`secure_post()` additionally takes a `json` argument, again mirroring the
`requests` library. Both return `requests.Response` objects upon successful
completion:
* `client.secure_get(endpoint, params=None)`  
    Make a secure `GET` request to the ListenFirst API.

* `client.secure_post(endpoint, json=None, params=None)`  
    Make a secure `POST` request to the ListenFirst API.

Commonly used endpoints have dedicated instance methods:
* `client.fetch(json)`  
    `POST` request to `/analytics/fetch` to perform a synchronous query.
 
* `client.create_fetch_job(json)`  
    `POST` request to `/analytics/fetch_job` to create an asynchronous query.

* `client.show_fetch_job(job_id)`  
    `GET` request to `/analytics/fetch_job/{id}` to view a summary of an
    existing asynchronous query. 
  
* `client.latest_fetch_job(params=None)`  
    `GET` request to `/analytics/fetch_job/latest` to view a summary of the most
    recent asynchronous query.

* `client.list_fetch_jobs(params=None)`  
    `GET` request to `/analytics/fetch_job` to view an abridged summary for all
    asynchronous queries.
 
* `client.create_schedule_config(json)`  
    `POST` request to `/analytics/schedule_config` to create an schedule
    configuration.
 
* `client.show_schedule_config(schedule_config_id)`  
    `GET` request to `/analytics/schedule_config/{id}` to view a summary of an
    existing schedule configuration.
 
* `client.list_schedule_configs(params=None)`  
    `GET` request to `/analytics/schedule_config` to view an abridged summary
    for all schedule configurations.
 
* `client.get_brand(brand_id, params=None)`  
    `GET` request to `/brand_views/{id}` to view a summary of a brand view.

* `client.list_brands(params=None)`  
    `GET` request to `/brand_views` to view a summary for all brand views.
 
* `client.get_brand_set(brand_set_id)`  
    `GET` request to `/brand_view_sets/{id}` to view a summary of a brand view
    set.
 
* `client.list_brand_sets(params=None)`  
    `GET` request to `/brand_view_sets` to view a summary for all brand view
    sets.
 
* `client.get_dataset(dataset_id)`  
    `GET` request to `/dictionary/datasets/{id}` to view a summary of a dataset.
 
* `client.list_datasets()`  
    `GET` request to `/dictionary/datasets` to view an abridged summary for all
     datasets.
 
* `client.get_field_values(params)`  
    `GET` request to `/dictionary/field_values` to view a list of values for a
    given field.

With the exception of `get_field_values()`, these methods wrap the API
responses in instances of `lfapi.Model` subclasses. These wrapper classes offer
some convenient extended functionality, such as JSON and CSV conversion.

In addition, the `Client` object implements a number of convenience methods
around the `/analytics` endpoints for managing data queries:
* `client.poll_fetch_job(job_id)`  
    Pull fetch job summary until state is one of 'completed', 'failed'.

* `client.sync_analytic_query(fetch_params, per_page=None, max_pages=inf)`  
    Run multiple pages of synchronous analytic queries.

* `client.async_analytic_query(fetch_params, client_context=None, max_rows=None, emails=None)`  
    Construct and poll an async analytic query, and download page URLs upon
    completion.

For code examples, see our [examples wiki](
https://github.com/ListenFirstMedia/lf-api-examples/wiki/Using-the-ListenFirst-API-Python-SDK).
