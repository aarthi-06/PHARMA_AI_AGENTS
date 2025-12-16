
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
import os

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")

# TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "..", "reporter", "templates")

def render_pdf(report_data: dict, output_path: str):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template("report.html.j2")

    html_content = template.render(report=report_data)

    HTML(string=html_content).write_pdf(output_path)
