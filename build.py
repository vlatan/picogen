import shutil
import logging
import jinja2 as jinja
from pathlib import Path
from slugify import slugify
from markdown import Markdown
from datetime import datetime
from dotenv import dotenv_values
from dataclasses import dataclass
from itertools import zip_longest

from config import Config


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


def autoversion_file(url: str) -> str:
    """Autoversion static files based on mtime."""

    filepath = Path("build/static") / Path(url).name
    timestamp = round(filepath.stat().st_mtime)

    return f"{url}?v={timestamp}"


def parse_markdown_file(path: Path, makrdown_instance: Markdown) -> dict:
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
    data["content"] = makrdown_instance.convert(content.strip())

    return data


def content_walk(path: Path) -> tuple[list[Path], list[Path]]:
    """
    Walk a dir and gather specific filepaths (pages and posts).
    Also Copy/paste posts/images dir.
    """

    pages_paths, posts_paths = [], []
    for root, dirs, files in path.walk():
        if str(root) == "content/posts/images":
            shutil.copytree(root, "build/posts/images")
            continue

        if str(root) == "content/pages":
            pages_paths = [root / fp for fp in files]
            continue

        if str(root) == "content/posts":
            posts_paths = [root / fp for fp in files]

    return posts_paths, pages_paths


def render_content(
    posts_paths: list[Path],
    pages_paths: list[Path],
    makrdown_instance: Markdown,
    jinja_env: jinja.Environment,
) -> None:
    """Parse and render all markdown content."""

    posts, pages, categories = set(), set(), set()
    for post_path, page_path in zip_longest(posts_paths, pages_paths):
        if post_path:
            data = parse_markdown_file(post_path, makrdown_instance)
            post = Post(**data)
            posts.add(post)
            categories.add(data.get("category"))

        if page_path:
            data = parse_markdown_file(page_path, makrdown_instance)
            page = Page(**data)
            pages.add(page)

    jinja_env.globals["categories"] = sorted(categories, key=lambda x: x.name)
    jinja_env.globals["pages"] = sorted(pages, key=lambda x: x.title)

    for post, page, category in zip_longest(posts, pages, categories):
        if post:
            post_template = jinja_env.get_template("post.html")
            parsed_post = post_template.render(post=post)
            post_dir_path = Path(f"build/posts/{post.slug}")
            post_dir_path.mkdir(exist_ok=True, parents=True)
            Path(post_dir_path / "index.html").write_text(parsed_post)

        if page:
            page_template = jinja_env.get_template("page.html")
            parsed_page = page_template.render(page=page)
            page_dir_path = Path(f"build/pages/{page.slug}")
            page_dir_path.mkdir(exist_ok=True, parents=True)
            Path(page_dir_path / "index.html").write_text(parsed_page)

        if category:
            cat_posts = [post for post in posts if post.category == category]
            cat_posts = sorted(cat_posts, key=lambda x: x.date, reverse=True)
            cat_template = jinja_env.get_template("category.html")
            parsed_cat = cat_template.render(category=category, posts=cat_posts)
            cat_dir_path = Path(f"build/categories/{category.slug}")
            cat_dir_path.mkdir(exist_ok=True, parents=True)
            Path(cat_dir_path / "index.html").write_text(parsed_cat)

    # render homepage
    sorted_posts = sorted(posts, key=lambda x: x.date, reverse=True)
    home_template = jinja_env.get_template("home.html")
    parsed_home = home_template.render(posts=sorted_posts)
    Path("build/index.html").write_text(parsed_home)

    # render 404 page
    not_found_template = jinja_env.get_template("404.html")
    parsed_not_found = not_found_template.render()
    Path("build/404.html").write_text(parsed_not_found)

    # render robots.txt
    robots_template = jinja_env.get_template("robots.txt")
    parsed_robots = robots_template.render()
    Path("build/robots.txt").write_text(parsed_robots)

    # render sitemap.xml
    sitemap_template = jinja_env.get_template("sitemap.xml")
    parsed_sitemap = sitemap_template.render(posts=sorted_posts)
    Path("build/sitemap.xml").write_text(parsed_sitemap)


if __name__ == "__main__":

    logging.getLogger().setLevel(logging.INFO)

    content_path = Path("content")
    if not content_path.is_dir():
        raise FileNotFoundError(f"No 'content' directory: '{content_path}'.")

    env_vars = {key: value for key, value in dotenv_values(".env").items() if value}
    cfg = Config(**env_vars)

    static_path = Path("themes") / cfg.THEME / "static"
    if not static_path.is_dir():
        msg = f"No 'static' directory in your theme: '{static_path}'."
        raise FileNotFoundError(msg)

    if cfg.THEME == "default":
        logging.info("Using the default theme.")

    # load theme's templates folder to Jinja's environment
    templates_path = Path("themes") / cfg.THEME / "templates"
    loader = jinja.FileSystemLoader(templates_path)
    jinja_env = jinja.Environment(
        trim_blocks=True,
        lstrip_blocks=True,
        autoescape=jinja.select_autoescape(),
        loader=loader,
    )
    jinja_env.globals["config"] = cfg
    jinja_env.filters["autoversion"] = autoversion_file

    # remove the build directory
    shutil.rmtree(Path("build"), ignore_errors=True)
    # include the static dir in the build
    shutil.copytree(static_path, "build/static")

    # get posts and pages path in content dir
    posts_paths, pages_paths = content_walk(content_path)
    # create markdown instance
    md = Markdown(extensions=["toc"], output_format="html")
    # parse and render all content
    render_content(posts_paths, pages_paths, md, jinja_env)

    # TODO: Copy or move the favicons to root
