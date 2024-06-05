import shutil
import pathlib
import logging
from markdown import markdown
from dotenv import dotenv_values
from jinja2 import Environment, FileSystemLoader, select_autoescape

from config import Config


logging.getLogger().setLevel(logging.INFO)


env_vars = {key: value for key, value in dotenv_values(".env").items() if value}
cfg = Config(**env_vars)

if cfg.THEME == "default":
    logging.info("No custom theme defined, using the default theme.")

templates = pathlib.Path("themes") / cfg.THEME / "templates"

# create the build directory if it doesn't exist
pathlib.Path("build").mkdir(exist_ok=True)

# load theme's templates folder to Jinja's environment
env = Environment(loader=FileSystemLoader(templates), autoescape=select_autoescape())

# load the `index.html` template
index_template = env.get_template("index.html")
parsed_index_template = index_template.render(title="Hello World", config=cfg)

static = pathlib.Path("themes") / cfg.THEME / "static"
if not static.is_dir():
    raise FileNotFoundError(f"No 'static' directory in your theme: '{static}'.")

# include the static dir in the build
try:
    shutil.copytree(static, "build/static")
except FileExistsError as err:
    shutil.rmtree("build/static")
    shutil.copytree(static, "build/static")

# TODO: Copy or move the favicons to root

# write the parsed template
pathlib.Path("build/index.html").write_text(parsed_index_template)
