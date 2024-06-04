import shutil
import pathlib
from markdown import markdown
from jinja2 import Environment, FileSystemLoader, select_autoescape

# make the build directory if it doesn't exist
pathlib.Path("build").mkdir(exist_ok=True)

# load templates folder to environment
env = Environment(loader=FileSystemLoader("templates"), autoescape=select_autoescape())

# load the `index.html` template
index_template = env.get_template("index.html")
parsed_index_template = index_template.render(title="Hello World")


# include the static dir in the build
try:
    shutil.copytree("static", "build/static")
except FileExistsError as err:
    shutil.rmtree("build/static")
    shutil.copytree("static", "build/static")


# write the parsed template
pathlib.Path("build/index.html").write_text(parsed_index_template)
