# Nanogen

A very simple static website generator that uses [Jinja](https://jinja.palletsprojects.com/en/3.1.x/) to generate your content.


## Prerequisites

* Create an `.env` file, as described in `example.env`
* Create a `content` directory

If you are using your own theme use the following structure. You can include aditional templates that extend or use these.

```
├── static
│   ├── css
│   └── images
└── templates
    ├── home.html               // homepage
    ├── post.html               // each article
    ├── page.html               // each page
    ├── category.html           // each category
    ├── 404.html                // 404 page
    ├── robots.txt              // robots file
    └── sitemap.xml             // sitemap
```

* Variables `posts`, `pages` and `categories` are made available to all `jinja` templates.
* Additionaly, single `post`, `page` and `category` variables are available in templates with the same names respectively.


## Build and Serve

```
python build.py && \
python -m http.server --directory build --bind localhost
```


## References:
- https://jinja.palletsprojects.com/en/3.1.x/


## TODO:
* Copy favicons to root
* Add maybe CLI for build and serve.
* Pagination?