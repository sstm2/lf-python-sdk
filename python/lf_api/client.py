from urllib.parse import urljoin, urlencode
from lf_api.auth import Auth
import lf_api.http_utils as http
from lf_api.errors import *
import json


class Client:
  """ListenFirst API v20200626 interface.

  Parameters:
  api_key
    the API key to be used
  auth
    the authentication object to be used for fetching access tokens
  account_id
    the acting account for requests; can be set to None for primary account use
  """

  API_HOST = 'https://listenfirst.io'
  API_VERSION = 'v20200626/'

  def __init__(self, api_key, auth, account_id):
    self.api_key = api_key
    self.auth = auth
    self.account_id = account_id


  # analytics methods
  def fetch(self, **kwargs):
    """POST request to /analytics/fetch to perform a synchronous query."""
    return self.secure_post('analytics/fetch', **kwargs)

  def create_fetch_job(self, **kwargs):
    """POST request to /analytics/fetch_job to create an asynchronous query."""
    return self.secure_post('analytics/fetch_job', **kwargs)

  def show_fetch_job(self, job_id, **kwargs):
    """GET request to /analytics/fetch_job/{id} to view a summary of an existing
    asynchronous query.
    """
    return self.secure_get(f'analytics/fetch_job/{job_id}', **kwargs)

  def latest_fetch_job(self, **kwargs):
    """GET request to /analytics/fetch_job/latest to view a summary of the most
    recent asynchronous query.
    """
    return self.secure_get('analytics/fetch_job/latest', **kwargs)

  def list_fetch_jobs(self, **kwargs):
    """GET request to /analytics/fetch_job to view an abridged summary for all
    asynchronous queries.
    """
    return self.secure_get('analytics/fetch_job', **kwargs)

  def create_schedule_config(self, **kwargs):
    """POST request to /analytics/schedule_config to create an schedule
    configuration.
    """
    return self.secure_post('analytics/schedule_config', **kwargs)

  def show_schedule_config(self, schedule_config_id, **kwargs):
    """GET request to /analytics/schedule_config/{id} to view a summary of an
    existing schedule configuration.
    """
    return self.secure_get(f'analytics/schedule_config/{schedule_config_id}', **kwargs)

  def list_schedule_configs(self, **kwargs):
    """GET request to /analytics/schedule_config to view an abridged summary for
    all asynchronous queries.
    """
    return self.secure_get('analytics/schedule_config', **kwargs)


  # brand methods
  def get_brand(self, brand_id, **kwargs):
    """GET request to /brand_views/{id} to view a summary of a brand view."""
    return self.secure_get(f'brand_views/{brand_id}', **kwargs)

  def list_brands(self, **kwargs):
    """GET request to /brand_views to view a summary for all brand views."""
    return self.secure_get('brand_views', **kwargs)


  # brand set methods
  def get_brand_set(self, brand_set_id, **kwargs):
    """GET request to /brand_view_sets/{id} to view a summary of a brand view
    set.
    """
    return self.secure_get(f'brand_view_sets/{brand_set_id}', **kwargs)

  def list_brand_sets(self, **kwargs):
    """GET request to /brand_view_sets to view a summary for all brand view set.
    """
    return self.secure_get('brand_view_sets', **kwargs)


  # dataset methods
  def get_dataset(self, dataset_id, **kwargs):
    """GET request to /dictionary/datasets/{id} to view a summary of a dataset.
    """
    return self.secure_get(f'dictionary/datasets/{dataset_id}', **kwargs)

  def list_datasets(self, **kwargs):
    """GET request to /dictionary/datasets to view an abridged summary for all
    datasets.
    """
    return self.secure_get('dictionary/datasets', **kwargs)


  # field values method
  def get_field_values(self, field_id, **kwargs):
    """GET request to /dictionary/field_values to view a list of values for a
    given field.
    """
    return self.secure_get(f'dictionary/field_values/{field_id}', **kwargs)



  # request methods
  def build_url(endpoint):
    # Build URL from an endpoint
    return urljoin(Client.API_HOST, Client.API_VERSION + endpoint)

  @property
  def headers(self):
    # Build headers object for ListenFirst API
    headers = {
      "content-type": 'application/json',
      "authorization": 'Bearer ' + self.auth.access_token,
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

  def secure_post(self, endpoint, data=None, params=None):
    """Make a secure POST request to the ListenFirst API."""
    return self._make_authorized_request(
      http.POST,
      endpoint,
      data=data,
      params=params
    )

  def _make_authorized_request(self, method, endpoint, **request_args):
    # Send authorized requests to the ListenFirst API
    url = Client.build_url(endpoint)
    request_args["headers"] = self.headers
    return http.make_request(method, url, **request_args)

  # Initialize from JSON
  @classmethod
  def load(cls, f):
    """Load a client from a JSON file."""
    if isinstance(f, str):
      with open(f) as f: return cls.load(f)

    profile = json.load(f)
    auth = Auth(profile["client_id"], profile["client_secret"])
    return cls(profile["api_key"], auth, profile.get("account_id"))
