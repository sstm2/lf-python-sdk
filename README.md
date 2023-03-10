
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

These credentials can be retrieved from [the platform's API settings page](
https://app.listenfirstmedia.com/#api).

Once instantiated, the `Client` object can be used to make customized HTTP requests to various API endpoints:

    res = c.secure_get('dictionary/datasets')

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

These methods wrap the API responses in instances of `lfapi.Model` subclasses.
These wrapper classes offer some convenient extended functionality, such as
JSON and CSV conversion.

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
