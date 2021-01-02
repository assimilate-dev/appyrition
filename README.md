# appyrition
API Client for the Ghost platform

This module provides a Python API Client for the Ghost content platform:
https://ghost.org/

It provides a set of functions to interact with the [Ghost Admin API
endpoints](https://ghost.org/docs/admin-api/#endpoints) which allow publishing
and updating posts.

The goal is to allow developers to create and track posts using local markdown
and git then deploy to Ghost without copying and pasting into the Ghost editor.

This module is tested only against V3 of the [Ghost Admin
API](https://ghost.org/docs/faq/api-versioning/).

## Installation

This package is not tested for production and is still in development. It will
remain on Github only until it is ready to be published.

```
pip install -e git://github.com/assimilate-dev/appyrition.git@v0.0.9000#egg=appyrition
```

## Initialize

Initialize using the basic information about your instance including a
`client_id` and `client_secret` created using
[custom integrations](https://ghost.org/integrations/custom-integrations/).

```
from appyrition import Ghost

gh = Ghost(
	'https://ghost.example.com',
	'v3',
	'CLIENT_ID',
	'CLIENT_SECRET'
)
```

Login using a specific user name and password. All subsequent actions will use
the permissions assigned to the
[user name role](https://ghost.org/help/managing-your-team/) you've used to sign in.

```
gh.login('username', 'password')
```

## Usage

Upload images.

```
gh.upload_image('images/image1.jpg', 'test/image1.jpg')
gh.upload_image('images/image2.png', 'test/image2.png')
```

With the images uploaded, use the URLs to reference images in your post.

```
post = {
  "title": "Test Post",
  "custom_excerpt": "Please ignore",
  "slug": "test-post",
  "feature_image": "https://ghost.example.com/content/images/2030/01/image1.jpg"
  "html": "<h2>Title 1</h2>\n<p>Test post. <img alt="Test Image" src="https://ghost.example.com/content/images/2030/01/image2.png" /></p>"
}

gh.create_post(post)
```

## Deploy

You can use `deploy` to create and test posts locally and then upload to Ghost
while maintaining a git-like workflow.

Create a post directory substituting your desired slug for `test-post`.

```
test-post
├── test-post.config
├── test-post.md
└── images
   └── image1.jpg
   └── image2.png
```

The config file should contain `title` at minimum. Currently this package only
supports HTML posts.

Reference all images using relative paths so that you can test locally.

This is an example config.

```
# test-post.config
{
  "title": "Test Post",
  "custom_excerpt": "Please ignore",
  "slug": "test-post",
  "feature_image": "images/test.jpg"
}
```

This is an example post using markdown.

```
## Title 1

This is a test post.

## Title 2

Please ignore this test image.

![Test Image](images/test.png)
```

Deploy will convert the markdown to HTML, combine it with the config file, then
upload all of the images and replace the local references with URLs. The post
will be made available as a draft unless you defined `"status": "published"` in
the config.

``` 
gh.deploy("C:/Users/mtreadwell/Documents/github/frostmaiden/posts/test-post")
```
