# post_and_page.py

import requests
import logging
import json

from markdown import markdown
from os import listdir, path

from .error import GhostException, AppyException
from .helpers import url_join


def _get(resource, search_type, base_url, session, resource_type):
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

  response = requests.get(url, cookies = session)

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
  response = _get(resource, search_type, base_url, session, resource_type)
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

  print(resource_json)

  if search_type == "id":
    resource_id = resource
  else:
    resource_id = resource_json["id"]

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


def _deploy(
  resource_dir,
  resource_type,
  update=False
):
  if resource_type == "posts":
    singular = "post"
  elif resource_type == "pages":
    singular = "page"
  else:
    raise AppyException(
      "resource_type must be one of 'posts' or 'pages'"
    )

  def os_normpath_join(p, b):
    f = path.normpath(path.join(p, b))
    return(f)

  resource_dir = path.normpath(path.abspath(resource_dir))
  logging.info(
    "Using {resource_dir} as {singular} directory".format(
      resource_dir = resource_dir,
      singular = singular
    )
  )

  base_name = path.basename(resource_dir)
  config_file_name = base_name + ".config"
  text_file_name = base_name + ".md"

  # handle config
  logging.info("Expecting config file %s", config_file_name)
  config_file_path = os_normpath_join(resource_dir, config_file_name)

  if path.exists(config_file_path):
    logging.info("Found config file")
    with open(config_file_path, encoding = "utf8") as config_file:
      try:
        resource = json.load(config_file)
      except ValueError:
        raise AppyException(
          config_file_name + " does not contain valid JSON"
        )
      except Exception as e:
        raise AppyException(
          "Unexpected error reading file " + config_file_name + ": " + e
        )
  else:
    raise AppyException(
      config_file_name + " does not exist"
    )

  # handle markdown
  logging.info(
    "Expecting {singular} file {text_file_name}".format(
      singular = singular,
      text_file_name = text_file_name
    )
  )

  resource_file_path = os_normpath_join(resource_dir, text_file_name)

  if path.exists(resource_file_path):
    logging.info("Found %s file", singular)
    with open(resource_file_path, encoding = "utf8") as resource_file:
      try:
        text = resource_file.read()
      except Exception as e:
        raise AppyException(
          "Unexpected error reading file {text_file_name}: {e}".format(
            text_file_name = text_file_name,
            e = e
          )
        )

  else:
    raise AppyException(
      "{text_file_name} does not exist".format(
        text_file_name = text_file_name
      )
    )

  # upload images
  image_dir = os_normpath_join(resource_dir, "images")

  if path.exists(image_dir):
    images = listdir(image_dir)
    logging.info("Found image directory %s", image_dir)

    if len(images) > 0:
      for image in images:
        image_path = "/".join(["images", image])

        in_text = image_path in text
        in_config = ("feature_image" in resource.keys()) & (resource["feature_image"] == image_path)

        if in_text | in_config:
          image_file = os_normpath_join(image_dir, image)
          upload = self.upload_image(
            image_file, "/".join(["images", base_name, image])
          )
          logging.info("Image uploaded: %s", image)

          image_meta = upload.json().get("images")[0]
          image_url = image_meta.get("url")
          logging.info("Image available at %s", image_url)

        if in_text:
          logging.info("Replacing local image reference with URL")
          text = text.replace(image_path, image_url)

        if in_config:
          resource["feature_image"] = resource["feature_image"].replace(
            image_path, image_url
          )

        if not in_text and not in_config:
          logging.warn(
            "Image {image_path} in directory but not referenced in {singular}".format(
              image_path = image_path,
              singular = singular
            )
          )

    else:
      logging.warn(
        "Images folder found but no images present; skipping image upload"
      )

  else:
    logging.info("Images folder not found; skipping image upload")

  html = markdown(text)
  resource.update({"html": html})

  if resource_type == "posts":
    if not update:
      response = self.create_post(resource)
    else:
      response = self.update_post(resource, resource["id"])
  elif resource_type == "pages":
    if not update:
      response = self.create_page(resource)
    else:
      response = self.update_page(resource, resource["id"])

  with open(resource_file_path, "w", encoding = "utf8") as f:
    f.write(text)

  resource.update({"id": response[resource_type][0]["id"]})
  resource.pop("html", None)

  with open(config_file_path, "w", encoding = "utf8") as f:
    json.dump(resource, f, indent=4, sort_keys=True)
  
  logging.info("Post successfully created")

  return response
