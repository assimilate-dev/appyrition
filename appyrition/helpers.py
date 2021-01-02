# helpers.py

def url_join(*args, end_slash = True):
	strip_args = [str(a).rstrip("/") for a in args]
	url = "/".join(strip_args)

	if end_slash and not url.endswith("/"):
		url = url + "/"

	return url
