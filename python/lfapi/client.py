import json
import time
import warnings
from math import inf
from urllib.parse import urljoin

import lfapi.http_utils as http
import lfapi.models as models
from lfapi.auth import Auth
from lfapi.errors import LfError


def throttle(sleep_time=1):
  def throttle_decorator(mth):
    last_call_time = -inf

    def _mth(*args, **kwargs):
      nonlocal last_call_time
      time_since_last_call = time.time() - last_call_time
      if 0 <= time_since_last_call < sleep_time:
        time.sleep(sleep_time - time_since_last_call)
      last_call_time = time.time()

      return mth(*args, **kwargs)

    return _mth

  return throttle_decorator

def as_model(model, listed=False):
  if not issubclass(model, models.Model):
    raise LfError('@as_model decorator takes a subclass of lfapi.Model')

  def as_model_decorator(mth):
    def _mth(self, *args, **kwargs):
      res = mth(self, *args, **kwargs)
      body = res.json()
      if listed:
        return models.ListModel(body, model, client=self)
      return model(body, client=self)

    return _mth

  return as_model_decorator

class Client:
  """ListenFirst API v20200626 interface.

  Parameters:
  api_key
    the API key to be used
  auth
    the authentication object to be used for fetching access tokens
  account_id
    the acting account for requests; can be set to None for primary account use
  api_host
    the host to send requests to; defaults to DEFAULT_API_HOST
  """

  DEFAULT_API_HOST = 'https://listenfirst.io'
  API_VERSION = 'v20200626/'

  def __init__(self, api_key, auth, account_id=None, api_host=None):
    self.api_key = api_key
    self.auth = auth
    self.account_id = account_id
    self.api_host = Client.DEFAULT_API_HOST if api_host is None else api_host


  # high-level querying method
  def analytic_query(self, dataset_id, start_date, end_date,
                     metrics=[],
                     group_by=[],
                     meta_dims=[],
                     filters=[],
                     sort=[],
                     sync=True,
                     per_page=None,
                     page=None,
                     num_pages=None,
                     include_total=False,
                     client_context=None,
                     max_rows=None,
                     emails=None):
    """Construct an analytic query powered by the /analytics/* family of
    endpoints.

    Arguments:
    dataset_id
      the API dataset to query
    start_date
      the beginning of the queried time window
    end_date
      the end of the queried time window
    metrics
      the list of metrics to query (optional)
    group_by
      the list of dimensions to group by (optional)
    meta_dims
      the list of additional dimensions to query (optional)
    filters
      the list of filters to apply to the query
    sort
      the list of fields to sort by
    sync
      whether to use the synchronous or asynchronous endpoint
    per_page
      the number of records per page; ignored if sync is False
    page
      the page to synchronously query; ignored if sync is False
    num_pages
      the number of pages to synchronously query, starting from 1; ignored if
      sync is False or if page is set
    include_total
      whether to request the total number of matching records; ignored if sync
      is False
    client_context
      the client context to pass to the fetch job; ignored if sync is True
    max_rows
      the max number of rows to asynchronously fetch; ignored if sync is True
    emails
      a list of emails to send the fetch job results to upon completion
      (optional); ignored if sync is True
    """
    # Build fetch request param hash
    fetch_params = {
      "dataset_id": dataset_id,
      "start_date": start_date,
      "end_date": end_date,
      "metrics": metrics,
      "group_by": group_by,
      "meta_dimensions": meta_dims,
      "filters": filters,
      "sort": sort
    }

    if sync:  # Perform a synchronous analytic query
      # Ignore fetch job arguments
      async_params = {
        "client_context": client_context,
        "max_rows": max_rows,
        "emails": emails
      }
      async_params = [p for p in async_params if async_params[p] is not None]
      if len(async_params) > 0:
        warnings.warn(f'Ignoring fetch job args: {", ".join(async_params)}')

      # Build base request body
      base_params = fetch_params
      if per_page is not None:
        base_params["per_page"] = per_page

      # Handle page arguments
      if page is not None:
        if num_pages is not None:
          warnings.warn('pages argument was passed; ignoring num_pages')
        params_list = [{**base_params, "page": page}]
      elif num_pages is not None:
        params_list = [{**base_params, "page": page}
                       for page in range(1, num_pages + 1)]
      else:
        params_list = [{**base_params}]

      # Only pass include_total flag to first request to avoid repeating
      # the expensive operation
      if include_total is True:
        params_list[0]["include_total"] = True

      # Generate pages
      pages = [self.fetch(params) for params in params_list]

    else:  # Perform an asynchronous analytic query
      # Ignore paging arguments
      page_params = {
        "per_page": per_page,
        "page": page,
        "num_pages": num_pages,
      }
      page_params = [p for p in page_params if page_params[p] is not None]
      if len(page_params) > 0:
        warnings.warn(f'Ignoring page args: {", ".join(page_params)}')

      # Build request body
      params = {"fetch_params": fetch_params}
      if client_context is not None:
        params["client_context"] = client_context
      if max_rows is not None:
        params["max_rows"] = max_rows
      if emails is not None:
        params["email_to"] = emails

      # Create and poll the fetch job
      fj = self.create_fetch_job(params)
      fj.poll()
      if fj.state == 'failed':
        msg = f'Fetch job {fj.id} failed during execution'
        raise LfError(msg)

      # Read the page urls from the response
      pages = fj.download_pages()

    return pages


  # analytics methods
  @throttle()
  @as_model(models.AnalyticResponse)
  def fetch(self, json):
    """POST request to /analytics/fetch to perform a synchronous query."""
    return self.secure_post('analytics/fetch', json=json)

  @throttle()
  @as_model(models.FetchJob)
  def create_fetch_job(self, json):
    """POST request to /analytics/fetch_job to create an asynchronous query."""
    return self.secure_post('analytics/fetch_job', json=json)

  @throttle()
  @as_model(models.FetchJob)
  def show_fetch_job(self, job_id):
    """GET request to /analytics/fetch_job/{id} to view a summary of an
    existing asynchronous query.
    """
    return self.secure_get(f'analytics/fetch_job/{job_id}')

  @throttle()
  @as_model(models.FetchJob)
  def latest_fetch_job(self, params=None):
    """GET request to /analytics/fetch_job/latest to view a summary of the most
    recent asynchronous query.
    """
    return self.secure_get('analytics/fetch_job/latest', params=params)

  @throttle()
  @as_model(models.FetchJob, listed=True)
  def list_fetch_jobs(self, params=None):
    """GET request to /analytics/fetch_job to view an abridged summary for all
    asynchronous queries.
    """
    return self.secure_get('analytics/fetch_job', params=params)

  @throttle()
  @as_model(models.ScheduleConfig)
  def create_schedule_config(self, json):
    """POST request to /analytics/schedule_config to create an schedule
    configuration.
    """
    return self.secure_post('analytics/schedule_config', json=json)

  @throttle()
  @as_model(models.ScheduleConfig)
  def show_schedule_config(self, schedule_config_id):
    """GET request to /analytics/schedule_config/{id} to view a summary of an
    existing schedule configuration.
    """
    return self.secure_get(f'analytics/schedule_config/{schedule_config_id}')

  @throttle()
  @as_model(models.ScheduleConfig, listed=True)
  def list_schedule_configs(self, params=None):
    """GET request to /analytics/schedule_config to view an abridged summary
    for all schedule configurations.
    """
    return self.secure_get('analytics/schedule_config', params=params)


  # brand methods
  @throttle()
  @as_model(models.Brand)
  def get_brand(self, brand_id, params=None):
    """GET request to /brand_views/{id} to view a summary of a brand view."""
    return self.secure_get(f'brand_views/{brand_id}', params=params)

  @throttle()
  @as_model(models.Brand, listed=True)
  def list_brands(self, params=None):
    """GET request to /brand_views to view a summary for all brand views."""
    return self.secure_get('brand_views', params=params)


  # brand set methods
  @throttle()
  @as_model(models.BrandSet)
  def get_brand_set(self, brand_set_id):
    """GET request to /brand_view_sets/{id} to view a summary of a brand view
    set.
    """
    return self.secure_get(f'brand_view_sets/{brand_set_id}')

  @throttle()
  @as_model(models.BrandSet, listed=True)
  def list_brand_sets(self, params=None):
    """GET request to /brand_view_sets to view a summary for all brand view
    sets.
    """
    return self.secure_get('brand_view_sets', params=params)


  # dataset methods
  @throttle()
  @as_model(models.Dataset)
  def get_dataset(self, dataset_id):
    """GET request to /dictionary/datasets/{id} to view a summary of a dataset.
    """
    return self.secure_get(f'dictionary/datasets/{dataset_id}')

  @throttle()
  @as_model(models.Dataset, listed=True)
  def list_datasets(self):
    """GET request to /dictionary/datasets to view an abridged summary for all
    datasets.
    """
    return self.secure_get('dictionary/datasets')


  # field values method
  @throttle()
  def get_field_values(self, params):
    """GET request to /dictionary/field_values to view a list of values for a
    given field.
    """
    return self.secure_get('dictionary/field_values', params=params)



  # request methods
  def _build_url(self, endpoint):
    # Build URL from an endpoint
    return urljoin(self.api_host, Client.API_VERSION + endpoint)

  @property
  def headers(self):
    # Build headers object for ListenFirst API
    headers = {
      "content-type": 'application/json',
      "authorization": f'Bearer {self.auth.access_token}',
      "x-api-key": self.api_key,
      "lf-client-library": 'Python SDK',
      "lf-client-version": '1.0.0'
    }
    if self.account_id is not None:
      headers["lfm-acting-account"] = self.account_id

    return headers

  @throttle()
  def secure_get(self, endpoint, params=None):
    """Make a secure GET request to the ListenFirst API."""
    return self._make_authorized_request(
      http.GET,
      endpoint,
      params=params
    )

  @throttle()
  def secure_post(self, endpoint, json=None, params=None):
    """Make a secure POST request to the ListenFirst API."""
    return self._make_authorized_request(
      http.POST,
      endpoint,
      json=json,
      params=params
    )

  @throttle()
  def _make_authorized_request(self, method, endpoint, **request_args):
    # Send authorized requests to the ListenFirst API
    url = self._build_url(endpoint)
    request_args["headers"] = self.headers
    return http.make_request(method, url, **request_args)

  # Initialize from JSON
  @classmethod
  def load(cls, f):
    """Load a client from a JSON file."""
    if isinstance(f, str):
      with open(f) as f:
        return cls.load(f)

    profile = json.load(f)
    auth = Auth(
      profile["client_id"],
      profile["client_secret"],
      auth_host=profile.get("auth_host")
    )
    return cls(
      profile["api_key"],
      auth,
      account_id=profile.get("account_id"),
      api_host=profile.get("api_host")
    )
