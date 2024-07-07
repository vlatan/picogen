# Picogen

A very simple static website generator that uses [Jinja](https://jinja.palletsprojects.com/en/3.1.x/) to generate your content.


## Prerequisites

Create/activate virtual environment and install the dependencies.

``` bash
python3 -m venv .venv &&
source .venv/bin/activate &&
pip install --upgrade pip &&
pip install -r requirements.txt
```

Create an `.env` file, as described in [example.env](example.env). If you are using your own theme use the following structure. Note, Inclusion of `sitemap.xsl` is optional. You can also include aditional templates that extend or use these.

```
├── static
│   ├── css
│   ├── favicons
│   └── images
└── templates
    ├── home.html       // homepage
    ├── post.html       // each article
    ├── page.html       // each page
    ├── category.html   // each category
    ├── 404.html        // 404 page
    ├── robots.txt      // robots file
    ├── sitemap.xml     // sitemap xml file
    └── sitemap.xsl     // sitemap xsl file (optional)
```

During the build, all the files in the `static/favicons` directory will be copied over to the root of the build too.

The `config` variable that containes the values from your `.env` file is available to all `jinja` templates. Also variables `posts`, `pages` and `categories` that contain all posts, pages and categories are available to all `jinja` templates. Additionaly, single `post`, `page` and `category` variables are available to the templates with the same names respectively.


## Writing Content

Create a `content` directory. Place your posts markdown files in a `posts` directory and your pages in the `pages` directory within the `content` directory. Include `images` directories within each post or page directory if necessary.

```
├── posts
│   ├── post-dir
│   │   ├── post.md
│   │   └── images
|   |       └── image.jpeg
│   └── post-dir
│       ├── post.md
│       └── images
|           └── image.jpeg
└── pages
    └── page-dir
        ├── page.md
        └── images
            └── image.jpeg
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

``` bash
python build.py && \
python -m http.server --directory build --bind localhost
```

The static site files and directories are generated within the `build` directory.

## Deploy to AWS

Run the [deploy.sh](deploy.sh) script with one argument that is the name of the AWS S3 bucket. This will synchronize the `build` directory with the designated S3 bucket (it will delete obsolete files in the bucket, and upload modified/new files), giving the static assets (images, css, js) cache-control metadata with large expire value, some assets with one day cache expiry, and everything else without any metadata.

``` bash
./deploy.sh example.com
```


## References:
- https://jinja.palletsprojects.com/en/3.1.x/


## TODO:
* Add maybe CLI for build and serve.
* Pagination


## License

[![License: MIT](https://img.shields.io/github/license/vlatan/nanogen?label=License)](/LICENSE "License: MIT")