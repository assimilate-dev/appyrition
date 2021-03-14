# post.py

from .post_and_page import _get, _create, _delete, _update
from .deploy import _deploy


def get_post(self, post=None, search_type="id", params = dict()):

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

  response = _get(
    post,
    search_type,
    params,
    self.base_url,
    self.session,
    resource_type = "posts"
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

  response = _create(
    post_json,
    self.base_url,
    self.session,
    resource_type = "posts"
  )

  

  return response


def update_post(self, new_post_json, post, search_type="id"):

  """
  Update a post in place.

  Existing post JSON is updated using dictionary `update()` method with new
  post JSON.

  Refer to valid post format: https://ghost.org/docs/admin-api/#the-post-object

  Parameters
  ----------
  new_post_json: dict
    The new post JSON
  post : str, optional
    ID or slug used to filter to a specific post
  search_type : str, optional
    Indicator for an ID search or a slug search
  """

  response = _update(
    new_post_json,
    post,
    search_type,
    self.base_url,
    self.session,
    resource_type = "posts"
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

  response = _delete(
    post,
    self.base_url,
    self.session,
    resource_type = "posts"
  )

  return response


def deploy_post(self, post_dir, update=False):
  response = _deploy(
    post_dir,
    "posts",
    self.base_url,
    self.session,
    update
  )

  return response
