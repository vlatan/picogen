import shutil
import logging
from pathlib import Path
from slugify import slugify
from markdown import Markdown
from datetime import datetime
from dotenv import dotenv_values
from dataclasses import dataclass
from jinja2 import Environment, FileSystemLoader, select_autoescape

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


def parse_content(posts_paths: list[Path], pages_paths: list[Path]) -> dict[str, set]:
    """Parse all markdown content."""

    posts, categories = set(), set()
    for post_path in posts_paths:
        data = parse_markdown_file(post_path, md)
        post = Post(**data)
        posts.add(post)
        categories.add(data.get("category"))

    pages, footer_pages = set(), set()
    for page_path in pages_paths:
        data = parse_markdown_file(page_path, md)
        page = Page(**data)
        if page.title in ["About", "Privacy"]:
            footer_pages.add(page)
        pages.add(page)

    return {
        "posts": posts,
        "categories": categories,
        "pages": pages,
        "footer_pages": footer_pages,
    }


def render_content(posts: set, pages: set, jinja_env: Environment) -> None:
    """Render all content to files."""

    # render posts
    for post in posts:
        post_template = jinja_env.get_template("post.html")
        parsed_post = post_template.render(post=post)
        post_dir_path = Path(f"build/posts/{post.slug}")
        post_dir_path.mkdir(exist_ok=True, parents=True)
        Path(post_dir_path / "index.html").write_text(parsed_post)

    # render pages
    for page in pages:
        page_template = jinja_env.get_template("page.html")
        parsed_page = page_template.render(page=page)
        page_dir_path = Path(f"build/pages/{page.slug}")
        page_dir_path.mkdir(exist_ok=True, parents=True)
        Path(page_dir_path / "index.html").write_text(parsed_page)

    # render homepage
    sorted_posts = sorted(posts, key=lambda x: x.date, reverse=True)
    home_template = jinja_env.get_template("home.html")
    parsed_home = home_template.render(posts=sorted_posts)
    Path("build/index.html").write_text(parsed_home)


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
    loader = FileSystemLoader(templates_path)
    jinja_env = Environment(loader=loader, autoescape=select_autoescape())
    jinja_env.globals["config"] = cfg

    # remove the build directory
    shutil.rmtree(Path("build"), ignore_errors=True)
    # include the static dir in the build
    shutil.copytree(static_path, "build/static")

    # create a markdown instance
    md = Markdown(extensions=["toc"], output_format="html")

    posts_paths, pages_paths = content_walk(content_path)
    parsed_content = parse_content(posts_paths, pages_paths)

    categories = parsed_content["categories"]
    footer_pages = parsed_content["footer_pages"]

    jinja_env.globals["categories"] = sorted(categories, key=lambda x: x.name)
    jinja_env.globals["footer_pages"] = sorted(footer_pages, key=lambda x: x.title)

    posts, pages = parsed_content["posts"], parsed_content["pages"]
    render_content(posts, pages, jinja_env)

    # TODO: Copy or move the favicons to root
    # TODO: aotoversion filter
    # TODO: category pages
