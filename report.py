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
    heading_tags = "h1,h2,h3,h4,h5,h6"
    for section in re.split(delimiter, main, flags=re.I):
        if not section.strip():
            continue
        section_html = BeautifulSoup(f"<h{section}", "html.parser")
        heading = section_html.select_one(heading_tags)
        heading_level = int(str(heading)[2:3])
        contents = "".join(str(tag) for tag in section_html.select(f":not({heading_tags})"))
        yield heading_level, heading, contents

def get_report_for_section(heading_level, heading, contents):
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

languages_and_sections = {
    language: list(get_sections_for_language(language))
    for language in languages
}
finished = {
    language: False for language in languages
}
current_index = {
    language: 0 for language in languages
}
current_heading_level = 0
rows = []

while not all(finished.values()):
    row = []
    for language in languages:
        if current_index[language] >= len(languages_and_sections[language]):
            finished[language] = True
            row.append("")
            continue

        heading_level, heading, contents = languages_and_sections[language][current_index[language]]

        if heading_level >= current_heading_level:
            row.append(
                get_report_for_section(heading_level, heading, contents)
            )
            current_index[language] += 1

            if heading_level > current_heading_level:
                current_heading_level += 1
        else:
            row.append("")

    if all(column == "" for column in row):
        current_heading_level -= 1

    rows.append(row)


print(template.render(rows=rows))