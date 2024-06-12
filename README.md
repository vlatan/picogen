# Nanogen

A very simple static website generator that uses [Jinja](https://jinja.palletsprojects.com/en/3.1.x/) to generate your content.


## Prerequisites

* Create/activate virtual environment and install the dependencies.
    ``` bash
    python3 -m venv .venv &&
    source .venv/bin/activate &&
    pip install --upgrade pip &&
    pip install -r requirements.txt
    ```

* Create an `.env` file, as described in `example.env`
* Create a `content` directory
* If you are using your own theme use the following structure. You can include aditional templates that extend or use these.

    ```
    ├── static
    │   ├── css
    │   ├── favicons
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

* Variables `posts`, `pages` and `categories` that contain all posts, pages and categories are made available to all `jinja` templates.
* Additionaly, single `post`, `page` and `category` variables are available in templates with the same names respectively.


## Writing Content

Place your posts markdown files in a `posts` directory and your pages in the `pages` directory within the content directory. Include `images` directories within them if necessary.

```
├── posts
│   ├── post.md
│   └── images
└── pages
    ├── page.md
    └── images
```


Every markdown file at the top needs to have a **metadata** section wrapped with `---`. The code will look for this section in each file and will warn you if something is missing. For example here's a post metadata:
```
---
Title: Here Goes the Title
Date: 2017-10-30 10:20
Modified: 2017-10-30 10:20
Category: Here Goes the Category
Image: /path/to/image.jpg
Slug: example-url-slug
---
```


## Build and Serve

```
python build.py && \
python -m http.server --directory build --bind localhost
```


## References:
- https://jinja.palletsprojects.com/en/3.1.x/


## TODO:
* Add maybe CLI for build and serve.
* Pagination


## License

[![License: MIT](https://img.shields.io/github/license/vlatan/nanogen?label=License)](/LICENSE "License: MIT")