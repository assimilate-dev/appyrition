# deploy.py

import logging
import json

from markdown import markdown
from os import listdir, path

from .error import AppyException
from .post_and_page import _create, _update
from .image import _upload_image


def get_singular(resource_type):
  if resource_type == "posts":
    singular = "post"
  elif resource_type == "pages":
    singular = "page"
  else:
    raise AppyException(
      "resource_type must be one of 'posts' or 'pages'"
    )

  return singular


def os_normpath_join(p, b):
  f = path.normpath(path.join(p, b))
  return(f)


def get_dir_structure(resource_dir):
  dir_str = {}
  resource_dir = path.normpath(path.abspath(resource_dir))
  dir_str["abs_path"] = resource_dir
  dir_str["base_name"] = path.basename(resource_dir)

  # config file path
  dir_str["config_file"] = os_normpath_join(
    resource_dir,
    dir_str["base_name"] + ".config"
  )

  logging.info(
    "Expecting config file {}".format(
      dir_str["config_file"]
    )
  )

  if not path.exists(dir_str["config_file"]):
    raise AppyException(
      "{} does not exist".format(dir_str["config_file"])
    )
  else:
    logging.info("Found config file")

  # markdown file path
  dir_str["md_file"] = os_normpath_join(
    resource_dir,
    dir_str["base_name"] + ".md"
  )

  logging.info(
    "Expecting md file {}".format(
      dir_str["md_file"]
    )
  )

  if not path.exists(dir_str["md_file"]):
    raise AppyException(
      "{} does not exist".format(dir_str["md_file"])
    )
  else:
    logging.info("Found md file")

  # image file paths
  dir_str["image_dir"] = os_normpath_join(resource_dir, "images")
  if not path.exists(dir_str["image_dir"]):
    logging.info("Images folder not found; image upload will be skipped")
    dir_str["image_dir_exists"] = False
  else:
    logging.info("Found image directory")
    dir_str["image_dir_exists"] = True
    dir_str["images"] = listdir(dir_str["image_dir"])

  return dir_str


def _deploy(
  resource_dir,
  resource_type,
  base_url,
  session,
  update=False
):
  singular = get_singular(resource_type)

  logging.info(
    "Using {resource_dir} as {singular} directory".format(
      resource_dir = resource_dir,
      singular = singular
    )
  )

  dir_str = get_dir_structure(resource_dir)

  # read config
  with open(dir_str["config_file"], encoding = "utf8") as c:
    try:
      resource = json.load(c)
    except ValueError:
      raise AppyException("Config file does not contain valid JSON")
    except Exception as e:
      raise AppyException(
        "Unexpected error reading file {config_file}: {e}".format(
          config_file = dir_str["config_file"],
          e = e
        )
      )
    
  # read markdown file
  with open(dir_str["md_file"], encoding = "utf8") as m:
    try:
      text = m.read()
    except Exception as e:
      raise AppyException(
        "Unexpected error reading file {md_file}: {e}".format(
          md_file = dir_str["md_file"],
          e = e
        )
      )

  # upload images
  # in addition to uploading the images to ghost
  # this code will replace local references (image/image_name.jpg) in both the
  # markdown and the feature image with the image url
  if dir_str["image_dir_exists"]:
    if len(dir_str["images"]) > 0:
      for image in dir_str["images"]:
        local_image_path = "/".join(["images", image])

        in_text = local_image_path in text
        has_feature_image = "feature_image" in resource.keys()
        is_feature_image = resource["feature_image"] == local_image_path
        in_config = has_feature_image & is_feature_image

        if in_text | in_config:
          abs_path_image = os_normpath_join(dir_str["image_dir"], image)
          upload = _upload_image(
            abs_path_image,
            "/".join(["images", dir_str["base_name"], image]),
            base_url,
            session
          )
          logging.info("Image uploaded: {}".format(image))

          image_meta = upload.json().get("images")[0]
          image_url = image_meta.get("url")
          logging.info("Image available at {}".format(image_url))

        if in_text:
          text = text.replace(local_image_path, image_url)

        if in_config:
          resource["feature_image"] = resource["feature_image"].replace(
            local_image_path, image_url
          )

        if not in_text and not in_config:
          logging.warn(
            "Image {path} in directory but not referenced in {singular}".format(
              path = local_image_path,
              singular = singular
            )
          )

    else:
      logging.warn(
        "Images folder found but no images present; skipping image upload"
      )


  html = markdown(text)
  resource.update({"html": html})

  if not update:
    response = _create(resource, base_url, session, resource_type)
  else:
    response = _update(
      resource,
      resource["id"],
      "id",
      base_url,
      session,
      resource_type
    )

  with open(dir_str["md_file"], "w", encoding = "utf8") as m:
    m.write(text)

  resource.update({"id": response[resource_type][0]["id"]})
  resource.pop("html", None)

  with open(dir_str["config_file"], "w", encoding = "utf8") as c:
    json.dump(resource, c, indent=4, sort_keys=True)
  
  logging.info("Post successfully created")

  return response
