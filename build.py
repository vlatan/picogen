from jinja2 import Template, Environment, FileSystemLoader, select_autoescape

# load templates folder to environment (security measure)
env = Environment(loader=FileSystemLoader("templates"), autoescape=select_autoescape())

# load the `index.jinja` template
index_template = env.get_template("index.html")
parsed_index_template = index_template.render(title="Hello World")

# write the parsed template
with open("build/index.html", "w") as home_page:
    home_page.write(parsed_index_template)
