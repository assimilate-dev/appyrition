# appyrition.py

import json
import requests
import logging
from os import listdir, path
from jwt import decode
from markdown import markdown
from mimetypes import MimeTypes

from .error import GhostException, AppyException
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

  deploy(post_dir)
    Gathers post text, config, and images from a directory and uploads the post
  """

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


  def get_post(self, post=None, search_type="id"):

    """
    Returns all posts or a filtered list of posts as JSON.

    If left at default, `post == None`, returns a JSON object containing all
    posts on the site.

    Posts can be filtered by providing either a post ID `search_type='slug'` or
    a post slug `search_type='id'`.

    Parameters
    ----------
    post : str, optional
      ID or slug used to filter to a specific post
    search_type : str, optional
      Indicator for an ID search or a slug search
    """

    if search_type not in ("id", "slug"):
      raise ValueError("search_type must be 'id' or 'slug'")

    url = url_join(self.base_url, "posts")

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

    response = requests.get(url, cookies = self.session)

    if response.status_code != 200:
      raise GhostException(
        response.status_code,
        response.json().get("errors", [])
      )

    return response


  def create_post(self, post_json):

    """
    Create a post.

    The API only supports uploading posts in mobiledoc or HTML format.

    For the minimum required configuration and appropriate JSON structure for
    `post_json` refer to the 'Source HTML' subsection of the 'Creating a Post'
    section of the Ghost Admin API docs:
    https://ghost.org/docs/admin-api/#creating-a-post

    This package currently only supports uploading posts as HTML. To convert
    from Markdown to HTML, use `from markdown import markdown`.
    Parameters
    ----------
    post_json : dict, optional
      Post JSON object
    """

    url = url_join(self.base_url, "posts")

    params = {"source": "html"}

    body = {"posts": [post_json]}

    response = requests.post(
      url,
      params = params,
      json = body,
      cookies = self.session
    )

    if response.status_code != 201:
      raise GhostException(
        response.status_code,
        response.json().get("errors", [])
      )

    return response


  def delete_post(self, post):

    """
    Remove a post by post ID.

    The API does not support removing a post by slug.

    Parameters
    ----------
    post : str, optional
      Post ID
    """

    url = url_join(self.base_url, "posts", post)

    response = requests.delete(url, cookies = self.session)

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

    url = url_join(self.base_url, "images", "upload")

    mime_type = MimeTypes().guess_type(file)[0]
    logging.debug("Using image mime type %s", mime_type)

    with open(file, "rb") as image:
      files = {"file": (file, image, mime_type), "ref": (None, ref, None)}
      response = requests.post(url, files = files, cookies = self.session)

    if response.status_code != 201:
      raise GhostException(
        response.status_code,
        response.json().get("errors", [])
      )
    
    return response


  def deploy(self, post_dir):

    """
    Combine configuration file, post markdown file, and local images located in
    a directory into a post.

    All files should be located in a single directory, e.g. test-post. The
    config and markdown files should match the directory name: test-post.config
    and test-post.md. Images should be stored in a subdirectory like
    test-post/images.

    To maintain a consistent local development pattern before deployment,
    reference all images in your markdown locally. This method will upload all
    images and replace local references with the uploaded image URL.

    Parameters
    ----------
    post_dir : str
      Path to image file
    """

    def os_normpath_join(p, b):
      f = path.normpath(path.join(p, b))
      return(f)

    post_dir = path.normpath(path.abspath(post_dir))
    logging.info("Using %s as post directory", post_dir)

    base_name = path.basename(post_dir)
    config_file_name = base_name + ".config"
    post_file_name = base_name + ".md"

    # handle post config
    logging.info("Expecting config file %s", config_file_name)
    config_file_path = os_normpath_join(post_dir, config_file_name)

    if path.exists(config_file_path):
      logging.info("Found config file")
      with open(config_file_path, encoding = "utf8") as config_file:
        try:
          post = json.load(config_file)
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

    # handle post markdown
    logging.info("Expecting post file %s", post_file_name)
    post_file_path = os_normpath_join(post_dir, post_file_name)

    if path.exists(post_file_path):
      logging.info("Found post file")
      try:
        post_file = open(post_file_path, encoding = "utf8")
      except Exception as e:
        raise AppyException(
          "Unexpected error reading file " + post_file_name + ": " + e
        )
      else:
        with post_file:
          text = post_file.read()
    else:
      raise AppyException(
        post_file_name + " does not exist"
      )

    # upload images
    image_file_path = os_normpath_join(post_dir, "images")

    if path.exists(image_file_path):
      images = listdir(image_file_path)
      logging.info("Found image directory %s", "/".join([base_name, "images"]))
      if len(images) > 0:
        for image in images:
          image_file = os_normpath_join(image_file_path, image)
          upload = self.upload_image(
            image_file, "/".join(["images", base_name, image])
          )
          logging.info("Image uploaded: %s", image)
          
          image_meta = upload.json().get("images")[0]
          image_url = image_meta.get("url")

          logging.info("Image available at %s", image_url)
          logging.info("Replacing local image reference with URL")

          text = text.replace("/".join(["images", image]), image_url)
          if "feature_image" in post.keys():
            post["feature_image"] = post["feature_image"].replace(
              "/".join(["images", image]), image_url
            )
      else:
        logging.warn(
          "Images folder found but no images present; skipping image upload"
        )
    else:
      logging.info("Images folder not found; skipping image upload")

    html = markdown(text)
    post.update({"html": html})

    self.create_post(post)
    logging.info("Post successfully created")
