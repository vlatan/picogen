# Netrewrite

## Build

```
python build.py
```


## Serve

If in Visual Studio Code you can click `Go Live` at the right bottom to run live server. Alternatively you can run a http server natively in Python.

```
python -m http.server --directory build
```

## TODO:

* Design templates.
* Add static files.
* Add content.
* Add maybe CLI for build and serve.
* Filter func to autoversion static files.
* Pagination?
* Walk the `content` folder recursively, find `.md` pages and render them with appropriate templates. 
  For example render `index.html` with `index.html` template, files in `pages` dir with `page.html`, files in `posts` with `post.html`, files in `categories` with `category.html` or categories can be rendered programmatically just with looking into every markdown file to see in which category it belongs.