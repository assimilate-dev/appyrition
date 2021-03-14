# page.py

from .post_and_page import _get, _create, _delete, _update
from .deploy import _deploy


def get_page(self, page=None, search_type="id", params=dict()):

  """
  Returns all pages or a filtered list of pages as JSON.

  If left at default, `page == None`, returns a JSON object containing all
  pages on the site.

  Pages can be filtered by providing either a page ID `search_type='slug'` or
  a page slug `search_type='id'`.

  Parameters
  ----------
  page : str
    ID or slug used to filter to a specific page
  search_type : str
    Indicator for an ID search or a slug search
  params : dict
    Search params for filtering
  """

  response = _get(
    page,
    search_type,
    params,
    self.base_url,
    self.session,
    resource_type = "pages"
  )

  return response


def update_page(self, new_page_json, page, search_type="id"):

  """
  Update a page in place.

  See `deploy_page(update=True)` before manually updating pages.

  Existing page JSON is updated using dictionary `update()` method with new
  page JSON.

  Refer to valid page format: https://ghost.org/docs/admin-api/#the-page-object

  Parameters
  ----------
  new_page_json: dict
    The new page JSON
  page : str
    ID or slug used to filter to a specific page
  search_type : str, optional
    Indicator for an ID search or a slug search
  """

  response = _update(
    new_page_json,
    page,
    search_type,
    self.base_url,
    self.session,
    resource_type = "pages"
  )

  return response


def create_page(self, page_json):

  """
  Create a page.

  See `deploy_page()` before manually creating pages.

  The API only supports uploading pages in mobiledoc or HTML format.

  For the minimum required configuration and appropriate JSON structure for
  `page_json` refer to the 'Source HTML' subsection of the 'Creating a Page'
  section of the Ghost Admin API docs:
  https://ghost.org/docs/admin-api/#creating-a-post

  This package currently only supports uploading pages as HTML. To convert
  from Markdown to HTML, use `from markdown import markdown`.

  Parameters
  ----------
  page_json : dict
    Page JSON object
  """

  response = _create(
    page_json,
    self.base_url,
    self.session,
    resource_type = "pages"
  )

  return response


def delete_page(self, page):

  """
  Remove a page by page ID.

  The API does not support removing a page by slug.

  Parameters
  ----------
  page : str
    Page ID
  """

  response = _delete(
    page,
    self.base_url,
    self.session,
    resource_type = "pages"
  )

  return response


def deploy_page(self, page_dir = ".", update=False):

  """
  Create or update a page from markdown and config files in a directory.

  See README for more details.

  Parameters
  ----------
  page_dir : str
    Directory containing page files
  update : bool
    If true, update an existing page. If false, create new page.
  """

  response = _deploy(
    page_dir,
    "pages",
    self.base_url,
    self.session,
    update
  )

  return response
