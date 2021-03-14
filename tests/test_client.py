import json
from appyrition import Ghost
from shutil import copytree, copyfile, rmtree
from markdown import markdown
import configparser

config = configparser.ConfigParser()
config.read("creds.ini")

gh = Ghost(
  "https://frostmaiden.assimilate.dev",
  "v3",
  config["ghost"]["client_id"],
  config["ghost"]["client_secret"]
)


def test_login():
  login = gh.login(
    config["ghost"]["username"],
    config["ghost"]["password"]
  )
  assert login.status_code == 201


def test_deploy_post_create():
  src = "test_post_create"
  dest = "test_post_create_copy"
  copytree(src, dest)

  f = "/".join([dest, dest]) + ".md"
  with open(f, encoding = "utf8") as m:
    text = m.read()

  html = markdown(text)

  response = gh.deploy_post(dest)
  assert response["posts"][0]["feature_image"].startswith("https://")

  params = {"formats": "html"}
  response = gh.get_post("test-post", search_type = "slug", params = params)
  assert response["posts"][0]["html"] == html.replace("\n", "")


def test_deploy_post_update():
  f = "test_post_create_copy/test_post_create_copy.config"
  with open(f, encoding = "utf8") as c:
    resource = json.load(c)

  resource["custom_excerpt"] = "Please ignore this!"

  with open(f, "w", encoding = "utf8") as c:
    json.dump(resource, c, indent=4, sort_keys=True)

  md_src = "test_post_update/test_post_create_copy.md"
  md_dest = "test_post_create_copy/test_post_create_copy.md"
  copyfile(md_src, md_dest)

  with open(md_dest, encoding = "utf8") as m:
    text = m.read()

  # response = gh.deploy_post("test_post_create_copy")

  html = markdown(text)

  response = gh.deploy_post("test_post_create_copy", update = True)
  assert response["posts"][0]["custom_excerpt"] == "Please ignore this!"

  params = {"formats": "html"}
  response = gh.get_post("test-post", search_type = "slug", params = params)
  print(response["posts"][0]["html"])
  print(html.replace("\n", ""))
  assert response["posts"][0]["html"] == html.replace("\n", "")


def test_delete_post():
  f = "test_post_create_copy/test_post_create_copy.config"
  with open(f, encoding = "utf8") as c:
    resource = json.load(c)

  response = gh.delete_post(resource["id"])
  assert response.status_code == 204

  rmtree("test_post_create_copy")
