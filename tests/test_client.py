import json
import os
import types

import pytest
from utils import assert_is_list_model, assert_is_model

from lfapi.client import Client
from lfapi.errors import RecordNotFound, RequestInvalid, Unauthorized
from lfapi.models import (AnalyticResponse, Brand, BrandSet, Dataset, FetchJob,
                          ScheduleConfig)

# load bad client
profile_keys = {"API_KEY", "CLIENT_ID", "CLIENT_SECRET"}
opt_profile_keys = {"API_HOST", "AUTH_HOST", "ACCOUNT_ID"}

if os.environ.keys() >= profile_keys:  # Read from environment vars
  profile_keys |= opt_profile_keys & os.environ.keys()
  profile = {key.lower(): os.environ[key] for key in profile_keys}
  profile["api_key"] = 'x' * len(profile["api_key"])
  bad_client = Client.from_dict(profile)
else:  # Read from profile file
  bad_client = Client.load('./tests/config/bad_profile.json')


class TestClient:
  @pytest.fixture(scope="class")
  def bad_fetch_params(self, fetch_params):
    bfp = {**fetch_params}
    del bfp['group_by']
    return bfp

  # analytics methods
  @pytest.mark.vcr
  def test_fetch_works(self, client, fetch_params):
    assert_is_model(client.fetch(json=fetch_params), AnalyticResponse)

  @pytest.mark.vcr
  def test_fetch_fails_for_bad_query(self, client, bad_fetch_params):
    with pytest.raises(RequestInvalid):
      client.fetch(json=bad_fetch_params)

  @pytest.mark.vcr
  def test_create_and_show_fetch_job_works(self, client, fetch_params,
                                           client_context):
    job = assert_is_model(
      client.create_fetch_job(json={
        "fetch_params": fetch_params,
        "client_context": client_context
      }),
      FetchJob
    )

    assert_is_model(client.show_fetch_job(job.id), FetchJob)

  @pytest.mark.vcr
  def test_list_fetch_jobs_works(self, client):
    assert_is_list_model(client.list_fetch_jobs(), FetchJob)

  @pytest.mark.vcr
  def test_create_fetch_job_fails_for_bad_query(self, client, bad_fetch_params,
                                                client_context):
    with pytest.raises(RequestInvalid):
      client.create_fetch_job(json={
        "fetch_params": bad_fetch_params,
        "client_context": client_context
      })

  @pytest.mark.vcr
  def test_show_fetch_job_fails_for_bad_id(self, client):
    jobs = assert_is_list_model(client.list_fetch_jobs(),
                                FetchJob)

    bad_id = min([job.id for job in jobs]) - 1
    with pytest.raises(RequestInvalid):
      client.show_fetch_job(bad_id)

  @pytest.mark.vcr
  def test_bare_latest_fetch_job_works(self, client):
    assert_is_model(client.latest_fetch_job(), FetchJob)

  @pytest.mark.vcr
  def test_filtered_latest_fetch_job_works(self, client, client_context):
    job = assert_is_model(
      client.latest_fetch_job(params={
        "client_context": client_context
      }),
      FetchJob
    )
    assert job.client_context == client_context

  @pytest.mark.vcr
  def test_filtered_latest_fetch_job_fails_for_bad_cc(self, client):
    jobs = assert_is_list_model(client.list_fetch_jobs(), FetchJob)

    contexts = sorted(
      {job.client_context for job in jobs if job.client_context is not None}
    )
    # Because every client context is a strict substring of bad_context (thanks
    # to the 'bad' suffix), we can be assured that no available client context
    # is equal to bad_context.
    bad_context = ''.join(contexts) + 'bad'
    with pytest.raises(RequestInvalid):
      client.latest_fetch_job(params={"client_context": bad_context})

  @pytest.mark.vcr
  def test_create_and_show_schedule_config_works(self, client, fetch_params,
                                                 client_context):
    config = assert_is_model(
      client.create_schedule_config(json={
        "fetch_params": fetch_params,
        "client_context": client_context,
        "cron_expression": "0 0 * * *",
        "num_times": 1
      }),
      ScheduleConfig
    )

    assert_is_model(client.show_schedule_config(config.id),
                    ScheduleConfig)

  @pytest.mark.vcr
  def test_list_schedule_configs_works(self, client):
    assert_is_list_model(client.list_schedule_configs(), ScheduleConfig)

  @pytest.mark.vcr
  def test_sync_analytic_query_works(self, client, fetch_params):
    max_pages = 1
    per_page = 10

    pages = client.sync_analytic_query(fetch_params, per_page=per_page,
                                       max_pages=max_pages)

    assert isinstance(pages, types.GeneratorType)
    page = next(pages)
    assert_is_model(page, AnalyticResponse)
    assert len(page) <= per_page
    with pytest.raises(StopIteration):  # Check number of pages
      next(pages)

  @pytest.mark.vcr
  def test_async_analytic_query_works(self, client, fetch_params):
    max_rows = 10

    pages = client.async_analytic_query(fetch_params, max_rows=max_rows)

    assert isinstance(pages, types.GeneratorType)
    num_rows = 0
    for page in pages:
      assert_is_model(page, AnalyticResponse)
      num_rows += len(page)
    assert num_rows <= max_rows


  # brand methods
  @pytest.mark.vcr
  def test_get_brand_works(self, client, brand_id):
    assert_is_model(client.get_brand(brand_id), Brand)

  @pytest.mark.vcr
  def test_list_brands_works(self, client):
    assert_is_list_model(client.list_brands(), Brand)

  @pytest.mark.vcr
  def test_get_brand_fails_for_bad_id(self, client):
    brands = assert_is_list_model(client.list_brands(params={
      "sort": json.dumps([
        {
          "field": "lfm.brand_view.id",
          "dir": "ASC"
        }
      ])
    }), Brand)

    bad_id = min([brand.id for brand in brands]) - 1
    with pytest.raises(RecordNotFound):
      client.get_brand(bad_id)


  # brand set methods
  @pytest.mark.vcr
  def test_get_brand_set_works(self, client, brand_set_id):
    assert_is_model(client.get_brand_set(brand_set_id), BrandSet)

  @pytest.mark.vcr
  def test_list_brand_sets_works(self, client):
    assert_is_list_model(client.list_brand_sets(), BrandSet)

  @pytest.mark.vcr
  def test_get_brand_set_fails_for_bad_id(self, client):
    brand_sets = assert_is_list_model(client.list_brand_sets(), BrandSet)

    bad_id = min([brand_set.id for brand_set in brand_sets]) - 1
    with pytest.raises(RecordNotFound):
      client.get_brand_set(bad_id)


  # dataset methods
  @pytest.mark.vcr
  def test_get_dataset_works(self, client):
    assert_is_model(client.get_dataset('dataset_brand_listenfirst'),
                    Dataset)

  @pytest.mark.vcr
  def test_list_datasets_works(self, client):
    assert_is_list_model(client.list_datasets(), Dataset)

  @pytest.mark.vcr
  def test_get_dataset_fails_for_bad_id(self, client):
    bad_id = 'dataset_brand_listenlast'
    with pytest.raises(RequestInvalid):
      client.get_dataset(bad_id)


  # field values method
  @pytest.mark.vcr
  def test_get_field_values_works(self, client):
    res = client.get_field_values({"field": 'lfm.brand.name'})
    assert res.status_code == 200

  @pytest.mark.vcr
  def test_get_field_values_fails_for_bad_field(self, client):
    with pytest.raises(RequestInvalid):
      client.get_field_values({"field": 'lfm.brand.name!'})

  @pytest.mark.vcr
  def test_get_field_values_fails_for_unlistable_field(self, client):
    with pytest.raises(RequestInvalid):
      client.get_field_values({"field": 'lfm.brand_view.id'})


class TestBadClient:
  @pytest.mark.vcr
  def test_request_fails(self, client, fetch_params):
    with pytest.raises(Unauthorized):
      bad_client.fetch(json=fetch_params)
