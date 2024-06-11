# Nano Static Website Generator

## Prerequisites

* Create an `.env` file, as described in `example.env`
* Create a `content` directory

If you are using your own theme that theme must contain a `static` directory as well as the following templates:
* 404.html
* category.html
* home.html
* page.html
* post.html
* robots.txt
* sitemap.xml

## Build and Serve

```
python build.py && \
python -m http.server --directory build --bind localhost
```

## References:
- https://jinja.palletsprojects.com/en/3.1.x/


## TODO:

* sitemap.xml
* Copy favicons to root
* Add maybe CLI for build and serve.
* Pagination?