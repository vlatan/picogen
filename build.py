import shutil
import pathlib
import logging
from markdown import markdown
from dotenv import dotenv_values
from jinja2 import Environment, FileSystemLoader, select_autoescape
from jinja2.exceptions import TemplateNotFound


logging.getLogger().setLevel(logging.INFO)


config = dotenv_values(".env")
theme = config.get("ACTIVE_THEME")
if not (theme := config.get("ACTIVE_THEME")):
    logging.info("No active theme defined, using the default theme.")
    theme = "default"

templates = pathlib.Path("themes") / theme / "templates"

# create the build directory if it doesn't exist
pathlib.Path("build").mkdir(exist_ok=True)

# load theme's templates folder to Jinja's environment
env = Environment(loader=FileSystemLoader(templates), autoescape=select_autoescape())


# load the `index.html` template
index_template = env.get_template("index.html")
parsed_index_template = index_template.render(title="Hello World", config=config)


static = pathlib.Path("themes") / theme / "static"
if not static.is_dir():
    raise FileNotFoundError(f"No 'static' directory in your theme: '{static}'.")


# include the static dir in the build
try:
    shutil.copytree(static, "build/static")
except FileExistsError as err:
    shutil.rmtree("build/static")
    shutil.copytree(static, "build/static")


# write the parsed template
pathlib.Path("build/index.html").write_text(parsed_index_template)
