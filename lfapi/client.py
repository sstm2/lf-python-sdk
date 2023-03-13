import json
from functools import wraps
from math import inf
from urllib.parse import urljoin

import lfapi.http_utils as http
import lfapi.models as models
from lfapi.auth import Auth
from lfapi.errors import LfError


def as_model(model, listed=False):
  # Convert HTTP responses to lfapi.Model subclass
  if not issubclass(model, models.Model):
    raise LfError('@as_model decorator takes a subclass of lfapi.Model')

  def as_model_decorator(mth):
    @wraps(mth)
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


  # analytics methods
  @as_model(models.AnalyticResponse)
  def fetch(self, json):
    """POST request to /analytics/fetch to perform a synchronous query."""
    return self.secure_post('analytics/fetch', json=json)

  @as_model(models.FetchJob)
  def create_fetch_job(self, json):
    """POST request to /analytics/fetch_job to create an asynchronous query."""
    return self.secure_post('analytics/fetch_job', json=json)

  @as_model(models.FetchJob)
  def show_fetch_job(self, job_id):
    """GET request to /analytics/fetch_job/{id} to view a summary of an
    existing asynchronous query.
    """
    return self.secure_get(f'analytics/fetch_job/{job_id}')

  @as_model(models.FetchJob)
  def latest_fetch_job(self, params=None):
    """GET request to /analytics/fetch_job/latest to view a summary of the most
    recent asynchronous query.
    """
    return self.secure_get('analytics/fetch_job/latest', params=params)

  @as_model(models.FetchJob, listed=True)
  def list_fetch_jobs(self, params=None):
    """GET request to /analytics/fetch_job to view an abridged summary for all
    asynchronous queries.
    """
    return self.secure_get('analytics/fetch_job', params=params)

  @as_model(models.ScheduleConfig)
  def create_schedule_config(self, json):
    """POST request to /analytics/schedule_config to create an schedule
    configuration.
    """
    return self.secure_post('analytics/schedule_config', json=json)

  @as_model(models.ScheduleConfig)
  def show_schedule_config(self, schedule_config_id):
    """GET request to /analytics/schedule_config/{id} to view a summary of an
    existing schedule configuration.
    """
    return self.secure_get(f'analytics/schedule_config/{schedule_config_id}')

  @as_model(models.ScheduleConfig, listed=True)
  def list_schedule_configs(self, params=None):
    """GET request to /analytics/schedule_config to view an abridged summary
    for all schedule configurations.
    """
    return self.secure_get('analytics/schedule_config', params=params)

  # high-level analytic query convenience utilities
  @as_model(models.FetchJob)
  def poll_fetch_job(self, job_id):
    """Pull fetch job summary until state is one of 'completed', 'failed'."""

    return http.retry(
      self.secure_get,
      max_tries=inf,
      max_wait_time=60 * 90,
      delay=1,
      retry_condition=lambda r: r.json()["record"]["state"] not in [
        'completed',
        'failed'
      ]
    )(f'analytics/fetch_job/{job_id}')

  def sync_analytic_query(self, fetch_params, per_page=None, max_pages=inf):
    """Run multiple pages of synchronous analytic queries.

    Arguments:
    fetch_params
      the query parameters; must include dataset_id, start_date, end_date, and
      filters entries, also accepts metrics, group_by, meta_dimensions, and
      sort
    per_page
      the number of rows to include in each page (optional)
    max_pages
      the max number of pages to synchronously fetch (optional)

    Returns:
      generator of requested pages as models.AnalyticResponse objects
    """
    # Build request body
    params = {**fetch_params}
    if per_page is not None:
      params["per_page"] = per_page

    # Yield each page
    page = 1
    while page <= max_pages:
      ar = self.fetch({**params, "page": page})
      yield ar
      if ar.is_last_page:
        return
      page += 1

  def async_analytic_query(self, fetch_params, client_context=None,
                           max_rows=None, emails=None):
    """Construct and poll an async analytic query, and download page URLs upon
    completion.

    Arguments:
    fetch_params
      the query parameters; must include dataset_id, start_date, end_date, and
      filters entries, also accepts metrics, group_by, meta_dimensions, and
      sort
    client_context
      the client context to pass to the fetch job
    max_rows
      the max number of rows to asynchronously fetch
    emails
      a list of emails to send the fetch job results to upon completion
      (optional)

    Returns:
      generator of downloaded pages as models.AnalyticResponse objects
    """
    # Build request body
    params = {"fetch_params": {**fetch_params}}
    if client_context is not None:
      params["client_context"] = client_context
    if max_rows is not None:
      params["max_rows"] = max_rows
    if emails is not None:
      params["email_to"] = emails

    # Create and poll the fetch job
    fj = self.create_fetch_job(params)
    fj = self.poll_fetch_job(fj.id)
    if fj.state == 'failed':
      msg = f'Fetch job {fj.id} failed during execution.'
      raise LfError(msg)

    # Read the page urls from the response
    return fj.download_pages()


  # brand methods
  @as_model(models.Brand)
  def get_brand(self, brand_id, params=None):
    """GET request to /brand_views/{id} to view a summary of a brand view."""
    return self.secure_get(f'brand_views/{brand_id}', params=params)

  @as_model(models.Brand, listed=True)
  def list_brands(self, params=None):
    """GET request to /brand_views to view a summary for all brand views."""
    return self.secure_get('brand_views', params=params)


  # brand set methods
  @as_model(models.BrandSet)
  def get_brand_set(self, brand_set_id):
    """GET request to /brand_view_sets/{id} to view a summary of a brand view
    set.
    """
    return self.secure_get(f'brand_view_sets/{brand_set_id}')

  @as_model(models.BrandSet, listed=True)
  def list_brand_sets(self, params=None):
    """GET request to /brand_view_sets to view a summary for all brand view
    sets.
    """
    return self.secure_get('brand_view_sets', params=params)


  # dataset methods
  @as_model(models.Dataset)
  def get_dataset(self, dataset_id):
    """GET request to /dictionary/datasets/{id} to view a summary of a dataset.
    """
    return self.secure_get(f'dictionary/datasets/{dataset_id}')

  @as_model(models.Dataset, listed=True)
  def list_datasets(self):
    """GET request to /dictionary/datasets to view an abridged summary for all
    datasets.
    """
    return self.secure_get('dictionary/datasets')


  # field values method
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

  def secure_get(self, endpoint, params=None):
    """Make a secure GET request to the ListenFirst API."""
    return self._make_authorized_request(
      http.GET,
      endpoint,
      params=params
    )

  def secure_post(self, endpoint, json=None, params=None):
    """Make a secure POST request to the ListenFirst API."""
    return self._make_authorized_request(
      http.POST,
      endpoint,
      json=json,
      params=params
    )

  def _make_authorized_request(self, method, endpoint, **request_args):
    # Send authorized requests to the ListenFirst API
    url = self._build_url(endpoint)
    request_args["headers"] = self.headers
    return http.make_request(method, url, **request_args)

  # Initialize from config
  @classmethod
  def from_dict(cls, profile):
    """Load a client from a dictionary."""
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

  @classmethod
  def load(cls, f):
    """Load a client from a JSON file."""
    if isinstance(f, str):
      with open(f) as f:
        return cls.load(f)

    profile = json.load(f)
    return cls.from_dict(profile)
