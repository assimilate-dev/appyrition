# appyrition.py

import json
import requests
import logging
from jwt import decode

from .error import GhostException
from .auth import generate_base_url, generate_auth_token
from .helpers import url_join


class Ghost(object):

  """
  A class used to represent a Ghost Administrator API session

  Attributes
  ----------
  version : str
    API version: currently only supports 'v3'
  site_url : str
    URL of your Ghost instance
  base_url : str
    Base URL for all Admin API requests to your Ghost instance
  client_id : str
    Admin API client ID
  client_secret : str
    Admin API client secret
  auth_token : str
    JSON web authorization token created using jwt.encode from pyjwt
  username : str
    Login user name to create session
  password : str
    Login password to create session
  session : requests.cookies.RequestsCookieJar
    Session cookie for the login

  Methods
  -------
  login(username, password)
    Creates a user session used for all subsequent API calls

  get_post(post=None, search_type="id")
    Returns all posts or a filtered list of posts as JSON

  create_post(post)
    Uploads a post as a draft

  delete_post(post)
    Remove a post

  upload_image(file, ref)
    Upload an image to be referenced by URL

  deploy(resource_dir)
    Gathers post text, config, and images from a directory and uploads the post
  """

  # imported methods
  from .post import get_post, create_post, delete_post, update_post, deploy_post
  from .page import get_page, create_page, delete_page, update_page, deploy_page
  from .image import upload_image
  from .site import get_site


  def __init__(
    self,
    site_url,
    version,
    client_id,
    client_secret
  ):

    """
    Parameters
    ----------
    site_url : str
      URL of your Ghost instance
    version : str
      API version: currently only supports 'v3'
    client_id : str
      Admin API client ID
    client_secret : str
      Admin API client secret
    """

    self.version = version
    self.site_url = site_url

    base_url = generate_base_url(site_url, version)
    self.base_url = base_url
    
    self.client_id = client_id
    self.client_secret = client_secret
    
    auth_token = generate_auth_token(client_id, client_secret)
    self.auth_token = auth_token

    self.username = None
    self.password = None
    self.session = None


  def login(self, username, password):

    """
    Creates a user session cookie used for all subsequent API calls.

    API access will be limited according to the role assigned to the logged-in
    user.

    Parameters
    ----------
    username : str
      Login user name to create session
    password : str
      Login password to create session
    """

    url = url_join(self.base_url, "session")

    payload = {
      "username": username,
      "password": password
    }

    headers = {
      "Authorization": "Ghost {}".format(
        decode(
          self.auth_token,
          bytes.fromhex(self.client_secret),
          algorithms=["HS256"],
          audience=["/{}/admin/".format(self.version)]
        )
      ),
      "Origin": "{}".format(self.site_url)
    }

    response = requests.post(url, data = payload, headers = headers)

    if response.status_code != 201:
      raise GhostException(
        response.status_code,
        response.json().get("errors", [])
      )

    self.username = username
    self.password = password
    self.session = response.cookies

    cookie = json.dumps(dict(response.cookies))
    logging.debug("Using session cookies: %s", cookie)

    return response
