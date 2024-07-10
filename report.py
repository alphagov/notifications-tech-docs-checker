import re
from jinja2 import Environment, FileSystemLoader

import requests
from bs4 import BeautifulSoup
environment = Environment(loader=FileSystemLoader("./"))
template = environment.get_template("report.jinja2")
languages = (
    "java",
    "net",
    "node",
    "php",
    "python",
    "ruby",
    "rest-api",
)

def get_sections_for_language(language):
    page = requests.get(f"https://docs.notifications.service.gov.uk/{language}.html")

    html = BeautifulSoup(page.content, "html.parser")

    main = str(html.select_one("main").decode_contents())
    delimiter = r"\<h"
    return re.split(delimiter, main, flags=re.I)

def get_report_for_section(section):
    if not section.strip():
        return ""
    heading_tags = "h1,h2,h3,h4,h5,h6"
    section_html = BeautifulSoup(f"<h{section}", "html.parser")
    heading = section_html.select_one(heading_tags)
    heading_level = str(heading)[2:3]
    contents = "".join(str(tag) for tag in section_html.select(f":not({heading_tags})"))
    if contents.strip():
        return f"""
            <div class="heading-level-{heading_level}">
                <details>
                    <summary>
                        {heading}
                    </summary>
                    <div class="contents">
                        {contents}
                    </div>
                </details>
            </div>
        """
    return f"""
        <div class="heading-level-{heading_level}">
            {heading}
        </div>
    """


languages_and_sections = [
    (
        language,
        [get_report_for_section(section) for section in get_sections_for_language(language)],
    )
    for language in languages
]


print(template.render(languages_and_sections=languages_and_sections))