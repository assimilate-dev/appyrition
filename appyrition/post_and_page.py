# post_and_page.py

import requests

from .error import GhostException, AppyException
from .helpers import url_join


def _get(resource, search_type, params, base_url, session, resource_type):
  if search_type not in ("id", "slug"):
    raise ValueError("search_type must be 'id' or 'slug'")

  url = url_join(base_url, resource_type)

  if search_type == "id":
    if resource is None:
      pass
    else:
      url = url_join(url, resource)
  else:
    if resource is None:
      raise ValueError(
        "'Must provide value for resource if search_type is 'slug'"
      )
    else:
      url = url_join(url, "slug", resource)        

  response = requests.get(url, params = params, cookies = session)

  if response.status_code != 200:
    raise GhostException(
      response.status_code,
      response.json().get("errors", [])
    )

  return response.json()


def _create(resource_json, base_url, session, resource_type):
  url = url_join(base_url, resource_type)
  params = {"source": "html"}
  body = {resource_type: [resource_json]}

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

  return response.json()


def _update(
  new_resource_json,
  resource,
  search_type,
  base_url,
  session,
  resource_type
):
  response = _get(
    resource,
    search_type,
    dict(),
    base_url,
    session,
    resource_type
  )
  resource_json = response[resource_type]

  if len(resource_json) > 1:
    raise AppyException(
      "Multiple posts at {search_type} {resource} found".format(
        search_type = search_type,
        resource = resource
      )
    )

  resource_json = resource_json[0]
  resource_json.update(new_resource_json)
  resource_json.pop("mobiledoc", None)

  if search_type == "id":
    resource_id = resource
  else:
    resource_id = resource_json["id"]

  if resource_type == "pages":
    resource_json.pop("comment_id", None)
    resource_json.pop("uuid", None)

  url = url_join(base_url, resource_type, resource_id)
  params = {"source": "html"}
  body = {resource_type: [resource_json]}

  response = requests.put(
    url,
    params = params,
    json = body,
    cookies = session
  )

  if response.status_code != 200:
    raise GhostException(
      response.status_code,
      response.json().get("errors", [])
    )

  return response.json()


def _delete(post, base_url, session, resource_type):
  url = url_join(base_url, resource_type, post)

  response = requests.delete(url, cookies = session)

  return response
