import pytest
from lf_api.client import Client
from lf_api.errors import *

brand_id = 6650
brand_set_id = 4626

client_context = 'lf_api pytest client context'

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
class TestClient:
  def setup_method(self):
    self.client = Client.load('./tests/config/test_profile.json')

  # analytics methods
  @pytest.mark.vcr
  def test_fetch_works(self):
    res = self.client.fetch(json=params1)
    assert res.status_code == 200

  @pytest.mark.vcr
  def test_fetch_fails_for_bad_query(self):
    with pytest.raises(RequestInvalid) as e:
      res = self.client.fetch(json=params2)

  @pytest.mark.vcr
  def test_create_and_show_fetch_job_works(self):
    res = self.client.create_fetch_job(json={
      "fetch_params": params1,
      "client_context": client_context
    })
    assert res.status_code == 200

    body = res.json()
    job_id = body["record"]["id"]
    res = self.client.show_fetch_job(job_id)
    assert res.status_code == 200

  @pytest.mark.vcr
  def test_list_fetch_jobs_works(self):
    res = self.client.list_fetch_jobs()
    assert res.status_code == 200

  @pytest.mark.vcr
  def test_create_fetch_job_fails_for_bad_query(self):
    with pytest.raises(RequestInvalid) as e:
      res = self.client.create_fetch_job(json={
        "fetch_params": params2,
        "client_context": client_context
      })

  @pytest.mark.vcr
  def test_show_fetch_job_fails_for_bad_id(self):
    list_resp = self.client.list_fetch_jobs()
    assert list_resp.status_code == 200

    job_ids = [rec["id"] for rec in list_resp.json()["records"]]
    bad_id = min(job_ids) - 1
    with pytest.raises(RequestInvalid) as e:
      res = self.client.show_fetch_job(bad_id)

  @pytest.mark.vcr
  def test_bare_latest_fetch_job_works(self):
    res = self.client.latest_fetch_job()
    assert res.status_code == 200

  @pytest.mark.vcr
  def test_filtered_latest_fetch_job_works(self):
    res = self.client.latest_fetch_job(params={"client_context": client_context})
    assert res.status_code == 200
    assert res.json()["record"]["client_context"] == client_context

  @pytest.mark.vcr
  def test_filtered_latest_fetch_job_fails_for_bad_cc(self):
    list_resp = self.client.list_fetch_jobs()
    assert list_resp.status_code == 200

    contexts = sorted(
      {rec["client_context"] for rec in list_resp.json()["records"]
        if rec["client_context"] is not None}
    )
    # Because every client context is a strict substring of bad_context (thanks
    # to the 'bad' suffix), we can be assured that no available client context
    # is equal to bad_context.
    bad_context = ''.join(contexts) + 'bad'
    with pytest.raises(RequestInvalid) as e:
      res = self.client.latest_fetch_job(params={"client_context": bad_context})

  @pytest.mark.vcr
  def test_create_and_show_schedule_config_works(self):
    res = self.client.create_schedule_config(json={
      "fetch_params": params1,
      "client_context": client_context,
      "cron_expression": "0 0 * * *",
      "num_times": 1
    })
    assert res.status_code == 200

    body = res.json()
    job_id = body["record"]["id"]
    res = self.client.show_schedule_config(job_id)
    assert res.status_code == 200

  @pytest.mark.vcr
  def test_list_schedule_configs_works(self):
    res = self.client.list_schedule_configs()
    assert res.status_code == 200


  # brand methods
  @pytest.mark.vcr
  def test_get_brand_works(self):
    res = self.client.get_brand(brand_id)
    assert res.status_code == 200

  @pytest.mark.vcr
  def test_list_brands_works(self):
    res = self.client.list_brands()
    assert res.status_code == 200

  @pytest.mark.vcr
  def test_get_brand_fails_for_bad_id(self):
    list_resp = self.client.list_brands()
    assert list_resp.status_code == 200

    brand_ids = [rec["id"] for rec in list_resp.json()["records"]]
    bad_id = min(brand_ids) - 1
    with pytest.raises(RecordNotFound) as e:
      res = self.client.get_brand(bad_id)


  # brand set methods
  @pytest.mark.vcr
  def test_get_brand_set_works(self):
    res = self.client.get_brand_set(brand_set_id)
    assert res.status_code == 200

  @pytest.mark.vcr
  def test_list_brand_sets_works(self):
    res = self.client.list_brand_sets()
    assert res.status_code == 200

  @pytest.mark.vcr
  def test_get_brand_set_fails_for_bad_id(self):
    list_resp = self.client.list_brand_sets()
    assert list_resp.status_code == 200

    brand_set_ids = [rec["id"] for rec in list_resp.json()["records"]]
    bad_id = min(brand_set_ids) - 1
    with pytest.raises(RecordNotFound) as e:
      res = self.client.get_brand_set(bad_id)


  # dataset methods
  @pytest.mark.vcr
  def test_get_dataset_works(self):
    res = self.client.get_dataset('dataset_brand_listenfirst')
    assert res.status_code == 200

  @pytest.mark.vcr
  def test_list_datasets_works(self):
    res = self.client.list_datasets()
    assert res.status_code == 200

  @pytest.mark.vcr
  def test_get_dataset_fails_for_bad_id(self):
    bad_id = 'dataset_brand_listenlast'
    with pytest.raises(RequestInvalid) as e:
      res = self.client.get_dataset(bad_id)


  # field values method
  @pytest.mark.vcr
  def test_get_field_values_works(self):
    res = self.client.get_field_values({"field": 'lfm.brand.name'})
    assert res.status_code == 200

  @pytest.mark.vcr
  def test_get_field_values_fails_for_bad_field(self):
    with pytest.raises(RequestInvalid) as e:
      res = self.client.get_field_values({"field": 'lfm.brand.name!'})

  @pytest.mark.vcr
  def test_get_field_values_fails_for_unlistable_field(self):
    with pytest.raises(RequestInvalid) as e:
      res = self.client.get_field_values({"field": 'lfm.brand_view.id'})


class TestBadClient:
  def setup_method(self):
    self.client = Client.load('./tests/config/bad_profile.json')

  @pytest.mark.vcr
  def test_reqest_fails(self):
    with pytest.raises(Unauthorized) as e:
      res = self.client.fetch(json=params1)

