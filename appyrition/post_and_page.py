# post_and_page.py

import requests
from .error import GhostException
from .helpers import url_join


def get_p(post, search_type, base_url, session, get_type):
  if search_type not in ("id", "slug"):
    raise ValueError("search_type must be 'id' or 'slug'")

  url = url_join(base_url, get_type)

  if search_type == "id":
    if post is None:
      pass
    else:
      url = url_join(url, post)
  else:
    if post is None:
      raise ValueError(
        "'Must provide value for post if search_type is 'slug'"
      )
    else:
      url = url_join(url, "slug", post)        

  response = requests.get(url, cookies = session)

  if response.status_code != 200:
    raise GhostException(
      response.status_code,
      response.json().get("errors", [])
    )

  return response


def create_p(post_json, base_url, session, get_type):
  url = url_join(base_url, get_type)

  params = {"source": "html"}

  body = {"posts": [post_json]}

  response = requests.post(
    url,
    params = params,
    json = body,
    cookies = session
  )

  if response.status_code != 201:
    raise GhostException(
      response.status_code,
      response.json().get("errors", [])
    )

  return response


def delete_p(post, base_url, session, get_type):
  url = url_join(base_url, get_type, post)

  response = requests.delete(url, cookies = session)

  return response
