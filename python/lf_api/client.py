from urllib.parse import urljoin, urlencode
from lf_api.auth import Auth
import lf_api.http_utils as http
from lf_api.errors import *
import json


class Client:
  API_HOST = 'https://listenfirst.io'
  API_VERSION = 'v20200626/'

  def __init__(self, api_key, auth, account_id):
    self.api_key = api_key
    self.auth = auth
    self.account_id = account_id


  # analytics methods
  def fetch(self, **kwargs):
    return self.secure_post('analytics/fetch', **kwargs)

  def create_fetch_job(self, **kwargs):
    return self.secure_post('analytics/fetch_job', **kwargs)

  def show_fetch_job(self, job_id, **kwargs):
    return self.secure_get(f'analytics/fetch_job/{job_id}', **kwargs)

  def latest_fetch_job(self, **kwargs):
    return self.secure_get('analytics/fetch_job/latest', **kwargs)

  def list_fetch_jobs(self, **kwargs):
    return self.secure_get('analytics/fetch_job', **kwargs)

  def create_schedule_config(self, **kwargs):
    return self.secure_post('analytics/schedule_config', **kwargs)

  def show_schedule_config(self, schedule_config_id, **kwargs):
    return self.secure_get(f'analytics/schedule_config/{schedule_config_id}', **kwargs)

  def list_schedule_configs(self, **kwargs):
    return self.secure_get('analytics/schedule_config', **kwargs)


  # brand methods
  def get_brand(self, brand_id, **kwargs):
    return self.secure_get(f'brand_views/{brand_id}', **kwargs)

  def list_brands(self, **kwargs):
    return self.secure_get('brand_views', **kwargs)


  # brand set methods
  def get_brand_set(self, brand_set_id, **kwargs):
    return self.secure_get(f'brand_view_sets/{brand_set_id}', **kwargs)

  def list_brand_sets(self, **kwargs):
    return self.secure_get('brand_view_sets', **kwargs)


  # dataset methods
  def get_dataset(self, dataset_id, **kwargs):
    return self.secure_get(f'dictionary/datasets/{dataset_id}', **kwargs)

  def list_datasets(self, **kwargs):
    return self.secure_get('dictionary/datasets', **kwargs)


  # field values method
  def get_field_values(self, field_id, **kwargs):
    return self.secure_get('dictionary/field_values', **kwargs)



  # request methods
  def build_url(endpoint):
    return urljoin(Client.API_HOST, Client.API_VERSION + endpoint)

  @property
  def headers(self):
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
    return self.make_authorized_request(
      http.GET,
      endpoint,
      params=params
    )

  def secure_post(self, endpoint, data=None, params=None):
    return self.make_authorized_request(
      http.POST,
      endpoint,
      data=data,
      params=params
    )

  def make_authorized_request(self, method, endpoint, **request_args):
    url = Client.build_url(endpoint)
    request_args["headers"] = self.headers
    return http.make_request(method, url, **request_args)

  # Initialize from JSON
  @classmethod
  def load(cls, f):
    if isinstance(f, str):
      with open(f) as f: return cls.load(f)

    profile = json.load(f)
    auth = Auth(profile["client_id"], profile["client_secret"])
    return cls(profile["api_key"], auth, profile.get("account_id"))
