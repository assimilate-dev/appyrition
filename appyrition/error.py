# error.py
# credit to rycus
# https://github.com/rycus86/ghost-client

class GhostException(Exception):
  """
  Type of exceptions raised by the client.
  """

  def __init__(self, code, errors):
    """
    Constructor.
    :param code: The HTTP status code returned by the API
    :param errors: The `errors` field returned in the response JSON
    """

    super(GhostException, self).__init__(code, errors)
    self.code = code
    self.errors = errors


class AppyException(Exception):
  """
  Type of exceptions raised by the library.
  """

  def __init__(self, errors):
    """
    Constructor.
    :param errors: The error
    """

    super(AppyException, self).__init__(errors)
    self.errors = errors
