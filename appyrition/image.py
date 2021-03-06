# image.py

import requests
import logging
from mimetypes import MimeTypes
from .error import GhostException
from .helpers import url_join


def _upload_image(file, ref, base_url, session):
  url = url_join(base_url, "images", "upload")

  mime_type = MimeTypes().guess_type(file)[0]
  logging.debug("Using image mime type %s", mime_type)

  with open(file, "rb") as image:
    files = {"file": (file, image, mime_type), "ref": (None, ref, None)}
    response = requests.post(url, files = files, cookies = session)

  if response.status_code != 201:
    raise GhostException(
      response.status_code,
      response.json().get("errors", [])
    )
  
  return response


def upload_image(self, file, ref):

  """
  Upload an image to be referenced by URL.

  The API does not support removing a post by slug.

  Parameters
  ----------
  file : str, optional
    Path to image file
  ref : str
    A reference for the image useful for finding images after uploads
  """

  response = _upload_image(file, ref, self.base_url, self.session)
  return response
