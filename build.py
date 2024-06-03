import shutil
import pathlib
import functools as ft
from jinja2 import Environment, FileSystemLoader, select_autoescape

# load templates folder to environment (security measure)
env = Environment(loader=FileSystemLoader("templates"), autoescape=select_autoescape())

# load the `index.html` template
index_template = env.get_template("index.html")
parsed_index_template = index_template.render(title="Hello World")


static_dir_source_path = "static"
copy_static_dir = ft.partial(shutil.copytree, static_dir_source_path, "build/static")

try:
    copy_static_dir()
except FileExistsError as err:
    shutil.rmtree("build/static")
    copy_static_dir()


# write the parsed template
pathlib.Path("build/index.html").write_text(parsed_index_template)
