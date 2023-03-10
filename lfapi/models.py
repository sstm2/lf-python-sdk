import csv
import importlib.util
import io
import json
from functools import wraps

import lfapi.http_utils as http
from lfapi.errors import LfError

if importlib.util.find_spec('pandas') is None:
  pd = None
else:
  import pandas as pd


class NoClientError(LfError):
  pass

def requires_client(mth):
  @wraps(mth)
  def _mth(self, *args, **kwargs):
    if self.client is None:
      raise NoClientError()

    return mth(self, *args, **kwargs)

  return _mth


class Model:
  """Superclass for ListenFirst API response wrappers.

  Parameters:
  body
    the API response body
  client
    the API client that generated the request; optional

  Attributes:
  record
    the "record" entry in the API response, if present
  """

  # Placeholder for required schema elements; should be specified in subclasses
  _required = []

  def __init__(self, body, client=None):
    self.body = body
    self.client = client

    cls = type(self)
    attr_dict = self.as_dict()
    missing = set(cls._required) - attr_dict.keys()
    msg = f'Missing attributes for {cls.__name__}: {", ".join(missing)}'
    assert not missing, msg

    for key, value in attr_dict.items():
      setattr(self, key, value)

  def as_dict(self):
    """Return the model as a dictionary."""
    return self.record if self.record is not None else self.body

  def to_json(self, fp=None, **json_kwargs):
    """Send the model to a JSON file or string object.

    Arguments:
    fp
      the file object or filename; if None, this method returns a string
      containing the data in JSON format
    **json_kwargs
      accepts any keyword arguments supported by json.dump()/json.dumps()
    """
    # Dump to string
    if fp is None:
      return json.dumps(self.as_dict(), **json_kwargs)

    # Convert filename to file pointer
    if isinstance(fp, str):
      with open(fp, 'w') as fp:
        return self.to_json(fp, **json_kwargs)

    # Defer to json.dump(), write to file
    return json.dump(self.as_dict(), fp, **json_kwargs)

  def merge(self, other):
    """Merge attributes of another model in-place."""
    assert type(self) is type(other)
    for attr in other.as_dict():
      setattr(self, attr, getattr(other, attr))


  @property
  def record(self):
    return self.body.get("record")


class FetchJob(Model):
  """Wrapper for ListenFirst API Fetch Jobs."""
  _required = ["id", "state", "created_at", "updated_at", "client_context",
               "schedule_config_id"]

  @requires_client
  def update(self):
    """Update fetch job via API."""
    self.merge(self.client.show_fetch_job(self.id))

  @requires_client
  def poll(self):
    """Update fetch job until state is one of 'completed', 'failed'."""
    self.merge(self.client.poll_fetch_job(self.id))

  def download_pages(self, label_mode="id"):
    """Return generator of fetch job's pages as AnalyticResponse objects."""
    if self.state != 'completed' or not hasattr(self, "page_urls"):
      raise LfError('Attempted to download pages from uncompleted fetch job.')

    return (AnalyticResponse(http.make_request(http.GET, url).json(),
                             label_mode=label_mode) for url in self.page_urls)


class ScheduleConfig(Model):
  """Wrapper for ListenFirst API Schedule Configs."""
  _required = ["id", "state", "created_at", "updated_at", "client_context"]

class Brand(Model):
  """Wrapper for ListenFirst API Brand Views."""
  _required = ["id", "name", "type", "dimensions"]

class BrandSet(Model):
  """Wrapper for ListenFirst API Brand View Sets."""
  _required = ["id", "name"]

class Dataset(Model):
  """Wrapper for ListenFirst API Datasets."""
  _required = ["id", "name", "description", "analysis_type", "dataset_type"]


class ListModel(Model):
  """Superclass for list-like ListenFirst API response wrappers.

  Parameters:
  item_class
    the class of list entries
  """

  _required = ["records"]

  def __init__(self, body, item_class, client=None):
    if not issubclass(item_class, Model):
      raise LfError(f'Expected Model class, got {item_class.__name__}')

    super().__init__(body, client=client)
    self._item_class = item_class
    self.records = [self._item_class(rec) for rec in self.records]

  def is_last_page(self):
    """Determine whether there are any remaining pages."""
    return not getattr(self, "has_more_pages")

  def as_list(self):
    """Return the model as a list."""
    return self.records

  def to_csv(self, fp=None, delimiter=','):
    """Send the model to a CSV file or string object.

    Arguments:
    fp
      the file object or filename; if None, this method returns a string
      containing the data in CSV format
    """
    # Set fp to string IO if not specified
    if fp is None:
      fp = io.StringIO()

    # Convert filename to file pointer
    if isinstance(fp, str):
      with open(fp, 'w') as fp:
        return self.to_csv(fp, delimiter=delimiter)

    # Write to fp
    rows = self.as_list()
    writer = csv.DictWriter(fp, delimiter=delimiter, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

    return fp.getvalue() if isinstance(fp, io.StringIO) else None

  def to_pandas(self):
    """Convert the model to a Pandas DataFrame. Not implemented if Pandas is
    not installed.
    """
    if pd is None:
      raise NotImplementedError('pandas is not installed.')

    rows = self.as_list()
    return pd.DataFrame(
      columns=rows[0].keys(),
      data=rows
    )

  # List-like dunder methods
  def __len__(self):
    return len(self.records)

  def __bool__(self):
    return len(self) > 0

  def __iter__(self):
    yield from self.as_list()

  def __add__(self, other):
    if not isinstance(other, ListModel):
      msg = f"'+' not supported between ListModel and {type(other).__name__}"
      raise LfError(msg)
    if self._item_class is not other._item_class:
      msg = "'+' not supported between ListModels with different item classes"
      raise LfError(msg)

    all_records = self.records + other.records
    body = {
      "records": [record.to_dict() for record in all_records]
    }
    return ListModel(body, self._item_class)


class AnalyticResponse(ListModel):
  """Wrapper for ListenFirst API Analytic Data."""

  _required = ["columns", "records"]

  def __init__(self, body, client=None, label_mode="id"):
    super(ListModel, self).__init__(body, client=client)
    if label_mode not in ["id", "name"]:
      raise LfError('Unexpected label_mode: "{label_mode}"')
    self.label_mode = label_mode

  def as_list(self):
    """Return the model as a list."""
    return [dict(zip(self._labels, row)) for row in self.records]

  def __add__(self, other):
    if not isinstance(other, AnalyticResponse):
      class_name = type(other).__name__
      msg = f"'+' not supported between AnalyticResponse and {class_name}"
      raise LfError(msg)
    if self.columns != other.columns:
      msg = "'+' not supported between AnalyticResponses with different schema"
      raise LfError(msg)

    body = {
      "columns": self.columns,
      "records": self.records + other.records
    }
    return AnalyticResponse(body, self._item_class)

  @property
  def _labels(self):
    # Return the list of column labels, using either "id" or "name"
    return [col[self.label_mode] for col in self.columns]
