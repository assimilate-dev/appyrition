# auth.py

from jwt import encode
from datetime import datetime as date


def generate_base_url(site_url, version):
  base_url = "{site_url}/ghost/api/{version}/admin/".format(
    site_url = site_url,
    version = version
  )

  return(base_url)


def generate_auth_header(
  client_id,
  iat = int(date.now().timestamp())
):
  header = {"alg": "HS256", "typ": "JWT", "kid": client_id}

  payload = {
    "iat": iat,
    "exp": iat + 5 * 60,
    "aud": "/v3/admin/"
  }

  return header, payload


def generate_auth_token(client_id, client_secret):
  header, payload = generate_auth_header(client_id)

  token = encode(
    payload,
    bytes.fromhex(client_secret),
    algorithm = "HS256",
    headers = header
  )

  return token
