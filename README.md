# Picogen

A very simple static website generator that uses [Jinja](https://jinja.palletsprojects.com/en/3.1.x/) to generate your content.


## Installation

Create/activate virtual environment and install `picogen` in your working directory.

``` bash
python3 -m venv .venv &&
source .venv/bin/activate &&
pip install --upgrade pip &&
pip install picogen
```

Optionally, to install the development dependencies use:
``` bash
pip install "picogen[dev]"
```

## Working Directory Structure

In your working directory you need to have the following structure where you'll have an `.env` file, a `content` directory in which you'll have your markdown files, and **optionally** if you don't use the default theme that ships with `picogen` you'll need a `themes` directory in which you'll have your own theme. You need to follow this exact same structure in order for `picogen` to know what to look where. Note, the inclusion of `sitemap.xsl` in your custom theme is optional. You can also include aditional templates that extend or use the existing templates.

```
├── .env
|
├── content
|   ├── posts
|   │   ├── post_1
|   │   │   ├── post.md
|   │   │   └── images
|   |   |       ├── image_1.jpeg
|   |   |       └── image_2.png
|   │   └── post_2
|   │       ├── post.md
|   │       └── images
|   |           └── image.jpeg
|   └── pages
|       └── page_1
|           ├── page.md
|           └── images
|               └── image.jpeg
|
└── themes                      // optional
    └── custom_theme
        ├── static
        │   ├── css
        │   ├── favicons
        │   └── images
        └── templates
            ├── home.html        // homepage
            ├── post.html        // each article
            ├── page.html        // each page
            ├── category.html    // each category
            ├── 404.html         // 404 page
            ├── robots.txt       // robots file
            ├── sitemap.xml      // sitemap xml file
            └── sitemap.xsl      // sitemap xsl file (optional)
```

## Config

The `.env` file should have the following content, out which all of the values are optional. If you use your own custom theme though you need to designate its directory name (`THEME`) in the `.env` file.

```
# .env file

SITE_URL=
SITE_NAME=
SITE_TAGLINE=

THEME=
GTAG_ID=
CONTACT_EMAIL=
```

## Writing Content

Every markdown file at the top needs to have a **metadata** section wrapped with `---`. `Picogen` will look for this section in each markdown file and will warn you if something is missing. For example here's a post metadata:
```
---
Title: Here Goes the Title
Date: 2017-10-30 10:20
Modified: 2017-10-30 10:20
Category: Here Goes the Category
Image: relative/path/to/image.jpg
Slug: example-url-slug
---
```

## Build, Serve, Deploy and Backup

Type `picogen -h` for help.
```
picogen [-h] [-g] [-d BUCKET_NAME] [-b BUCKET_NAME]
```

Examples to build, deploy and backup your website:

```
picogen --generate --deploy bucket_name --backup bucket_name
picogen -gd bucket_name -b bucket_name
```

`Picogen` has a baked in option for deployment and/or backup of your static website to AWS S3. You can ommit these functions simply by not using the flags `--deploy` and/or `--backup`. You can just use `picogen --generate` and `picogen` will look for your `content` directory and optionally your `themes/your-theme` directory and build the website into the `build` directory. Obviusly if you want to deploy and/or backup your website to AWS S3 you need to setup AWS CLI as well as S3 buckets, one for deployment and one for backing up your makrdown files.

Note, during the build, all the files in the `static/favicons` directory in your theme will be copied over to the root of the `build` too.

The `config` variable that containes the values from your `.env` file is available to all of the `jinja` templates. Also variables `posts`, `pages` and `categories` that contain all posts, pages and categories are available to all `jinja` templates. Additionaly, single `post`, `page` and `category` variables are available to the templates with the same names respectively.

To serve your website locally on port `8000` you can use:
```
python -m http.server --directory build --bind localhost
```


## References:
- https://jinja.palletsprojects.com/en/3.1.x/


## License

[![License: MIT](https://img.shields.io/github/license/vlatan/nanogen?label=License)](/LICENSE "License: MIT")