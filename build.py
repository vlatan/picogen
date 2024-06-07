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


env_vars = {key: value for key, value in dotenv_values(".env").items() if value}
cfg = Config(**env_vars)

if cfg.THEME == "default":
    logging.info("Using the default theme.")

templates = pathlib.Path("themes") / cfg.THEME / "templates"

# remove the build directory
shutil.rmtree(pathlib.Path("build"), ignore_errors=True)

# load theme's templates folder to Jinja's environment
env = Environment(loader=FileSystemLoader(templates), autoescape=select_autoescape())

static = pathlib.Path("themes") / cfg.THEME / "static"
if not static.is_dir():
    raise FileNotFoundError(f"No 'static' directory in your theme: '{static}'.")

# include the static dir in the build
shutil.copytree(static, "build/static")

content = pathlib.Path("content")
if not content.is_dir():
    raise FileNotFoundError(f"No 'content' directory: '{content}'.")


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


md = Markdown(extensions=["toc"], output_format="html")

# TODO: when using content.walk() just gather paths
# later iterate over them to render files because first we need pages

for root, dirs, files in content.walk():
    if str(root) == "content/posts/images":
        shutil.copytree(root, "build/posts/images")
        continue

    elif str(root) == "content/pages":
        pages = set()
        for fp in files:
            page_md = (root / fp).read_text().strip()
            _, meta, content = page_md.split("---")

            metadata = {}
            for line in meta.strip().splitlines():
                key, value = line.split(": ")
                if key in ["Date", "Modified"]:
                    value = datetime.strptime(value, "%Y-%m-%d %H:%M")
                metadata[key.lower()] = value

            metadata["content"] = md.convert(content.strip())
            page = Page(**metadata)
            pages.add(page)

        for page in pages:
            page_template = env.get_template("page.html")
            parsed_page = page_template.render(
                page=page,
                config=cfg,
            )

            # write the parsed post template to file
            page_dir_path = pathlib.Path(f"build/pages/{page.slug}")
            page_dir_path.mkdir(exist_ok=True, parents=True)
            pathlib.Path(page_dir_path / "index.html").write_text(parsed_page)

    elif str(root) == "content/posts":
        posts, categories = set(), set()
        for fp in files:
            post_md = (root / fp).read_text().strip()
            _, meta, content = post_md.split("---")

            metadata = {}
            for line in meta.strip().splitlines():
                key, value = line.split(": ")
                if key in ["Date", "Modified"]:
                    value = datetime.strptime(value, "%Y-%m-%d %H:%M")
                elif key == "Category":
                    value = Category(name=value, slug=slugify(value))
                metadata[key.lower()] = value

            paragraphs = content.strip().split("\n\n")

            sentences = (
                paragraphs[1].split(". ")
                if "/images/" in paragraphs[0]
                else paragraphs[0].split(". ")
            )

            # set as excerpt the first three sentences from the paragraph
            metadata["excerpt"] = ". ".join(sentences[:3]) + "."
            metadata["content"] = md.convert(content.strip())

            post = Post(**metadata)
            posts.add(post)
            categories.add(metadata.get("category"))

        # Sort categories alphabetically
        categories = sorted(categories, key=lambda x: x.name)
        # sort posts by date
        posts = sorted(posts, key=lambda x: x.date, reverse=True)

        for post in posts:
            post_template = env.get_template("post.html")
            parsed_post = post_template.render(
                post=post,
                categories=categories,
                pages=[],
                config=cfg,
            )

            # write the parsed post template to file
            post_dir_path = pathlib.Path(f"build/posts/{post.slug}")
            post_dir_path.mkdir(exist_ok=True, parents=True)
            pathlib.Path(post_dir_path / "index.html").write_text(parsed_post)


# TODO: Copy or move the favicons to root

footer_pages = [page for page in pages if page.title in ["About", "Privacy"]]
footer_pages = sorted(footer_pages, key=lambda x: x.title)
# load the `index.html` template
home_template = env.get_template("home.html")
parsed_home = home_template.render(
    categories=categories, posts=posts, pages=footer_pages, config=cfg
)

# write the parsed template
pathlib.Path("build/index.html").write_text(parsed_home)
