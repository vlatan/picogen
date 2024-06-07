import os
import shutil
import pathlib
import logging
from slugify import slugify
from markdown import Markdown
from datetime import datetime
from dotenv import dotenv_values
from dataclasses import dataclass
from jinja2 import Environment, FileSystemLoader, select_autoescape

from config import Config


logging.getLogger().setLevel(logging.INFO)


@dataclass(frozen=True)
class Category:
    name: str
    slug: str


@dataclass(frozen=True)
class Page:
    title: str
    date: datetime
    modified: datetime
    slug: str
    content: str


@dataclass(frozen=True)
class Post:
    title: str
    date: datetime
    modified: datetime
    category: Category
    image: str
    slug: str
    excerpt: str
    content: str


def parse_markdown(path: pathlib.Path) -> dict:
    """Take post or page markdown filepath and return a dict of necessary data."""

    md_content = path.read_text().strip()
    _, meta, content = md_content.split("---")

    data = {}
    for line in meta.strip().splitlines():
        key, value = line.split(": ")
        if key in ["Date", "Modified"]:
            data[key.lower()] = datetime.strptime(value, "%Y-%m-%d %H:%M")
            continue

        if key == "Category":
            # init Category object
            data[key.lower()] = Category(name=value, slug=slugify(value))

            # set as excerpt as the first three sentences from the paragraph
            paragraphs = content.strip().split("\n\n")
            sentences = (
                paragraphs[1].split(". ")
                if "/images/" in paragraphs[0]
                else paragraphs[0].split(". ")
            )
            data["excerpt"] = ". ".join(sentences[:3]) + "."
            continue

        data[key.lower()] = value

    # convert markdown to html
    data["content"] = md.convert(content.strip())

    return data


def content_walk(path: pathlib.Path) -> dict:
    """
    Walk a dir and gather specific filepaths (pages and posts).
    Also Copy/paste posts/images dir.
    """

    result = {}
    for root, dirs, files in path.walk():
        if str(root) == "content/posts/images":
            shutil.copytree(root, "build/posts/images")
            continue

        if str(root) == "content/pages":
            result["pages_paths"] = [root / fp for fp in files]
            continue

        if str(root) == "content/posts":
            result["posts_paths"] = [root / fp for fp in files]

    return result


content_path = pathlib.Path("content")
if not content_path.is_dir():
    raise FileNotFoundError(f"No 'content' directory: '{content_path}'.")

env_vars = {key: value for key, value in dotenv_values(".env").items() if value}
cfg = Config(**env_vars)

static_path = pathlib.Path("themes") / cfg.THEME / "static"
if not static_path.is_dir():
    raise FileNotFoundError(f"No 'static' directory in your theme: '{static_path}'.")

if cfg.THEME == "default":
    logging.info("Using the default theme.")

templates = pathlib.Path("themes") / cfg.THEME / "templates"

# load theme's templates folder to Jinja's environment
jinja_env = Environment(
    loader=FileSystemLoader(templates), autoescape=select_autoescape()
)
jinja_env.globals["config"] = cfg

# remove the build directory
shutil.rmtree(pathlib.Path("build"), ignore_errors=True)
# include the static dir in the build
shutil.copytree(static_path, "build/static")


md = Markdown(extensions=["toc"], output_format="html")


# TODO: Copy or move the favicons to root


content_filepaths = content_walk(content_path)

posts, categories = set(), set()
for post_path in content_filepaths["posts_paths"]:
    data = parse_markdown(post_path)
    post = Post(**data)
    posts.add(post)
    categories.add(data.get("category"))

pages, footer_pages = set(), set()
for page_path in content_filepaths["pages_paths"]:
    data = parse_markdown(page_path)
    page = Page(**data)
    if page.title in ["About", "Privacy"]:
        footer_pages.add(page)
    pages.add(page)

jinja_env.globals["categories"] = sorted(categories, key=lambda x: x.name)
jinja_env.globals["footer_pages"] = sorted(footer_pages, key=lambda x: x.title)

for post in posts:
    post_template = jinja_env.get_template("post.html")
    parsed_post = post_template.render(post=post)
    post_dir_path = pathlib.Path(f"build/posts/{post.slug}")
    post_dir_path.mkdir(exist_ok=True, parents=True)
    pathlib.Path(post_dir_path / "index.html").write_text(parsed_post)

for page in pages:
    page_template = jinja_env.get_template("page.html")
    parsed_page = page_template.render(page=page)
    page_dir_path = pathlib.Path(f"build/pages/{page.slug}")
    page_dir_path.mkdir(exist_ok=True, parents=True)
    pathlib.Path(page_dir_path / "index.html").write_text(parsed_page)

# create homepage
posts = sorted(posts, key=lambda x: x.date, reverse=True)
home_template = jinja_env.get_template("home.html")
parsed_home = home_template.render(posts=posts)
pathlib.Path("build/index.html").write_text(parsed_home)

# TODO: aotoversion filter
# TODO: category content pages
