# site.py

import requests
from .error import GhostException
from .helpers import url_join


def get_site(self):

  """
  Get basic site information.
  """

  url = url_join(self.base_url, "site")

  response = requests.get(url, cookies = self.session)

  if response.status_code != 200:
    raise GhostException(
      response.status_code,
      response.json().get("errors", [])
    )

  return response
