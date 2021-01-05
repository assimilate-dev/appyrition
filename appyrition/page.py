# page.py

from .post_and_page import get_p, create_p, delete_p


def get_page(self, page=None, search_type="id"):

  """
  Returns all pages or a filtered list of pages as JSON.

  If left at default, `page == None`, returns a JSON object containing all
  pages on the site.

  Pages can be filtered by providing either a page ID `search_type='slug'` or
  a page slug `search_type='id'`.

  Parameters
  ----------
  page : str, optional
    ID or slug used to filter to a specific page
  search_type : str, optional
    Indicator for an ID search or a slug search
  """

  response = get_p(
    page,
    search_type,
    self.base_url,
    self.session,
    get_type = "pages"
  )

  return response


def create_page(self, page_json):

  """
  Create a page.

  The API only supports uploading pages in mobiledoc or HTML format.

  For the minimum required configuration and appropriate JSON structure for
  `page_json` refer to the 'Source HTML' subsection of the 'Creating a Page'
  section of the Ghost Admin API docs:
  https://ghost.org/docs/admin-api/#creating-a-post

  This package currently only supports uploading pages as HTML. To convert
  from Markdown to HTML, use `from markdown import markdown`.
  Parameters
  ----------
  page_json : dict, optional
    Page JSON object
  """

  response = create_p(
    page_json,
    self.base_url,
    self.session,
    get_type = "pages"
  )

  return response


def delete_page(self, page):

  """
  Remove a page by page ID.

  The API does not support removing a page by slug.

  Parameters
  ----------
  page : str, optional
    Page ID
  """

  response = delete_p(page, self.base_url, self.session, get_type = "pages")

  return response
