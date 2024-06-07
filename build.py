import os
import shutil
import pathlib
import logging
from slugify import slugify
from markdown import markdown
from datetime import datetime
from dotenv import dotenv_values
from dataclasses import dataclass
from jinja2 import Environment, FileSystemLoader, select_autoescape

from config import Config


logging.getLogger().setLevel(logging.INFO)


env_vars = {key: value for key, value in dotenv_values(".env").items() if value}
cfg = Config(**env_vars)

if cfg.THEME == "default":
    logging.info("No custom theme defined, using the default theme.")

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
class Post:
    title: str
    date: datetime
    modified: datetime
    category: Category
    image: str
    slug: str
    excerpt: str
    content: str


for root, dirs, files in content.walk():
    if str(root) == "content/images":
        shutil.copytree(root, "build/images")
        continue

    if str(root) == "content/posts":
        posts, categories = set(), set()
        for fp in files:
            post_content = (root / fp).read_text().strip()
            _, meta, content = post_content.split("---")

            # TODO: these are potentially unbound
            for item in meta.strip().splitlines():
                if "Title: " in item:
                    title = item.split("Title: ")[-1]
                elif "Date: " in item:
                    date = item.split("Date: ")[-1]
                    date = datetime.strptime(date, "%Y-%m-%d %H:%M")
                elif "Modified: " in item:
                    modified = item.split("Modified: ")[-1]
                    modified = datetime.strptime(modified, "%Y-%m-%d %H:%M")
                elif "Category: " in item:
                    name = item.split("Category: ")[-1]
                    category = Category(name=name, slug=slugify(name))
                elif "Image: " in item:
                    image = item.split("Image: ")[-1]
                elif "Slug: " in item:
                    slug = item.split("Slug: ")[-1]

            paragraphs = content.strip().split("\n\n")
            if "/images/" in paragraphs[0]:
                sentences = paragraphs[1].split(". ")
                excerpt = ". ".join(sentences[:3]) + "."
            else:
                sentences = paragraphs[0].split(". ")
                excerpt = ". ".join(sentences[:3]) + "."

            post = Post(
                title=title,
                date=date,
                modified=modified,
                category=category,
                image=image,
                slug=slug,
                excerpt=excerpt,
                content=markdown(content),
            )

            posts.add(post)
            categories.add(category)

        # Sort categories alphabetically
        categories = sorted(categories, key=lambda x: x.name)
        # sort posts by date
        posts = sorted(posts, key=lambda x: x.date, reverse=True)

        for post in posts:
            # create dir in posts with post.slug name
            pathlib.Path(f"build/posts/{post.slug}").mkdir(exist_ok=True, parents=True)
            post_template = env.get_template("post.html")
            parsed_post = post_template.render(
                post=post,
                categories=categories,
                pages=[],
                config=cfg,
            )

            # write the parsed post template to file
            pathlib.Path(f"build/posts/{post.slug}/index.html").write_text(parsed_post)


# TODO: Copy or move the favicons to root
# TODO: Pass pages to templates to be used in footer

# load the `index.html` template
index_template = env.get_template("home.html")
parsed_index_template = index_template.render(
    categories=categories, posts=posts, pages=[], config=cfg
)

# write the parsed template
pathlib.Path("build/index.html").write_text(parsed_index_template)
