import os
import types

import pytest
from lfapi.client import Client
from lfapi.errors import RecordNotFound, RequestInvalid, Unauthorized
from lfapi.models import (AnalyticResponse, Brand, BrandSet, Dataset, FetchJob,
                          ListModel, Model, ScheduleConfig)

brand_id = os.environ.get("BRAND_ID")
brand_id = int(brand_id) if brand_id is not None else brand_id
brand_set_id = 4626  # My Brands

client_context = 'lfapi pytest client context'

params1 = {
  "dataset_id": 'dataset_brand_listenfirst',
  "start_date": '2022-07-10',
  "end_date": '2022-08-10',
  "group_by": [
    'lfm.brand_view.id'
  ],
  "metrics": [
    'lfm.post_engagement_score.comments_score_v5'
  ],
  "meta_dimensions": [
    'lfm.brand.name'
  ],
  "filters": [
    {
      "field": 'lfm.brand_view.id',
      "operator": 'IN',
      "values": [
        brand_id
      ]
    }
  ]
}

params2 = {
  "dataset_id": 'dataset_brand_listenfirst',
  "start_date": '2022-07-10',
  "end_date": '2022-08-10',
  "metrics": [
    'lfm.post_engagement_score.comments_score_v5'
  ],
  "meta_dimensions": [
    'lfm.brand.name'
  ],
  "filters": [
    {
      "field": 'lfm.brand_view.id',
      "operator": 'IN',
      "values": [
        brand_id
      ]
    }
  ]
}

def requires_brand_id(mth):
  def _mth(*args, **kwargs):
    if brand_id is None:
      print(f'No brand_id specified; skipping {mth.__name__}')
      return None
    return mth(*args, **kwargs)
  return _mth

def assert_is_model(obj, model):
  assert issubclass(model, Model)
  assert isinstance(obj, model)
  return obj

def assert_is_list_model(obj, item_class):
  obj = assert_is_model(obj, ListModel)
  assert obj._item_class is item_class
  return obj


class TestClient:
  def setup_method(self):
    profile_keys = {"API_KEY", "CLIENT_ID", "CLIENT_SECRET"}
    opt_profile_keys = {"API_HOST", "AUTH_HOST", "ACCOUNT_ID"}

    if os.environ.keys() >= profile_keys:  # Read from environment vars
      profile_keys |= opt_profile_keys & os.environ.keys()
      profile = {key.lower(): os.environ[key] for key in profile_keys}
      self.client = Client.from_dict(profile)

    else:  # Read from profile file
      self.client = Client.load('./tests/config/test_profile.json')

  # analytics methods
  @pytest.mark.vcr
  @requires_brand_id
  def test_fetch_works(self):
    assert_is_model(self.client.fetch(json=params1), AnalyticResponse)

  @pytest.mark.vcr
  @requires_brand_id
  def test_fetch_fails_for_bad_query(self):
    with pytest.raises(RequestInvalid):
      self.client.fetch(json=params2)

  @pytest.mark.vcr
  @requires_brand_id
  def test_create_and_show_fetch_job_works(self):
    job = assert_is_model(
      self.client.create_fetch_job(json={
        "fetch_params": params1,
        "client_context": client_context
      }),
      FetchJob
    )

    assert_is_model(self.client.show_fetch_job(job.id), FetchJob)

  @pytest.mark.vcr
  def test_list_fetch_jobs_works(self):
    assert_is_list_model(self.client.list_fetch_jobs(), FetchJob)

  @pytest.mark.vcr
  @requires_brand_id
  def test_create_fetch_job_fails_for_bad_query(self):
    with pytest.raises(RequestInvalid):
      self.client.create_fetch_job(json={
        "fetch_params": params2,
        "client_context": client_context
      })

  @pytest.mark.vcr
  def test_show_fetch_job_fails_for_bad_id(self):
    jobs = assert_is_list_model(self.client.list_fetch_jobs(),
                                FetchJob)

    bad_id = min([job.id for job in jobs]) - 1
    with pytest.raises(RequestInvalid):
      self.client.show_fetch_job(bad_id)

  @pytest.mark.vcr
  def test_bare_latest_fetch_job_works(self):
    assert_is_model(self.client.latest_fetch_job(), FetchJob)

  @pytest.mark.vcr
  def test_filtered_latest_fetch_job_works(self):
    job = assert_is_model(
      self.client.latest_fetch_job(params={
        "client_context": client_context
      }),
      FetchJob
    )
    assert job.client_context == client_context

  @pytest.mark.vcr
  def test_filtered_latest_fetch_job_fails_for_bad_cc(self):
    jobs = assert_is_list_model(self.client.list_fetch_jobs(), FetchJob)

    contexts = sorted(
      {job.client_context for job in jobs if job.client_context is not None}
    )
    # Because every client context is a strict substring of bad_context (thanks
    # to the 'bad' suffix), we can be assured that no available client context
    # is equal to bad_context.
    bad_context = ''.join(contexts) + 'bad'
    with pytest.raises(RequestInvalid):
      self.client.latest_fetch_job(params={"client_context": bad_context})

  @pytest.mark.vcr
  @requires_brand_id
  def test_create_and_show_schedule_config_works(self):
    config = assert_is_model(
      self.client.create_schedule_config(json={
        "fetch_params": params1,
        "client_context": client_context,
        "cron_expression": "0 0 * * *",
        "num_times": 1
      }),
      ScheduleConfig
    )

    assert_is_model(self.client.show_schedule_config(config.id),
                    ScheduleConfig)

  @pytest.mark.vcr
  def test_list_schedule_configs_works(self):
    assert_is_list_model(self.client.list_schedule_configs(), ScheduleConfig)

  @pytest.mark.vcr
  def test_sync_analytic_query_works(self):
    max_pages = 1
    per_page = 10

    pages = self.client.sync_analytic_query(params1, per_page=per_page,
                                            max_pages=max_pages)

    assert isinstance(pages, types.GeneratorType)
    page = next(pages)
    assert_is_model(page, AnalyticResponse)
    assert len(page) <= per_page
    with pytest.raises(StopIteration):  # Check number of pages
      next(pages)

  @pytest.mark.vcr
  def test_async_analytic_query_works(self):
    max_rows = 10

    pages = self.client.async_analytic_query(params1, max_rows=max_rows)

    assert isinstance(pages, types.GeneratorType)
    num_rows = 0
    for page in pages:
      assert_is_model(page, AnalyticResponse)
      num_rows += len(page)
    assert num_rows <= max_rows


  # brand methods
  @pytest.mark.vcr
  @requires_brand_id
  def test_get_brand_works(self):
    assert_is_model(self.client.get_brand(brand_id), Brand)

  @pytest.mark.vcr
  def test_list_brands_works(self):
    assert_is_list_model(self.client.list_brands(), Brand)

  @pytest.mark.vcr
  def test_get_brand_fails_for_bad_id(self):
    brands = assert_is_list_model(self.client.list_brands(), Brand)

    bad_id = min([brand.id for brand in brands]) - 1
    with pytest.raises(RecordNotFound):
      self.client.get_brand(bad_id)


  # brand set methods
  @pytest.mark.vcr
  def test_get_brand_set_works(self):
    assert_is_model(self.client.get_brand_set(brand_set_id), BrandSet)

  @pytest.mark.vcr
  def test_list_brand_sets_works(self):
    assert_is_list_model(self.client.list_brand_sets(), BrandSet)

  @pytest.mark.vcr
  def test_get_brand_set_fails_for_bad_id(self):
    brand_sets = assert_is_list_model(self.client.list_brand_sets(), BrandSet)

    bad_id = min([brand_set.id for brand_set in brand_sets]) - 1
    with pytest.raises(RecordNotFound):
      self.client.get_brand_set(bad_id)


  # dataset methods
  @pytest.mark.vcr
  def test_get_dataset_works(self):
    assert_is_model(self.client.get_dataset('dataset_brand_listenfirst'),
                    Dataset)

  @pytest.mark.vcr
  def test_list_datasets_works(self):
    assert_is_list_model(self.client.list_datasets(), Dataset)

  @pytest.mark.vcr
  def test_get_dataset_fails_for_bad_id(self):
    bad_id = 'dataset_brand_listenlast'
    with pytest.raises(RequestInvalid):
      self.client.get_dataset(bad_id)


  # field values method
  @pytest.mark.vcr
  def test_get_field_values_works(self):
    res = self.client.get_field_values({"field": 'lfm.brand.name'})
    assert res.status_code == 200

  @pytest.mark.vcr
  def test_get_field_values_fails_for_bad_field(self):
    with pytest.raises(RequestInvalid):
      self.client.get_field_values({"field": 'lfm.brand.name!'})

  @pytest.mark.vcr
  def test_get_field_values_fails_for_unlistable_field(self):
    with pytest.raises(RequestInvalid):
      self.client.get_field_values({"field": 'lfm.brand_view.id'})


class TestBadClient:
  def setup_method(self):
    profile_keys = {"API_KEY", "CLIENT_ID", "CLIENT_SECRET"}
    opt_profile_keys = {"API_HOST", "AUTH_HOST", "ACCOUNT_ID"}

    if os.environ.keys() >= profile_keys:  # Read from environment vars
      profile_keys |= opt_profile_keys & os.environ.keys()
      profile = {key.lower(): os.environ[key] for key in profile_keys}
      profile["api_key"] = 'x' * len(profile["api_key"])
      self.client = Client.from_dict(profile)

    else:  # Read from profile file
      self.client = Client.load('./tests/config/bad_profile.json')

  @pytest.mark.vcr
  @requires_brand_id
  def test_request_fails(self):
    with pytest.raises(Unauthorized):
      self.client.fetch(json=params1)
