import re
from pathlib import Path
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup
from jinja2 import Environment, FileSystemLoader
from notifications_utils.timezones import utc_string_to_aware_gmt_datetime


environment = Environment(loader=FileSystemLoader("./"))
report_template = environment.get_template("report.jinja2")
index_template = environment.get_template("index.jinja2")
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
        heading = str(section_html.select_one(heading_tags))
        heading_level = int(str(heading)[2:3])
        for heading_in_contents in section_html.select(heading_tags):
            heading_in_contents.decompose()
        contents = str(section_html)
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
    current_heading_level += 1

    for language in languages:
        if current_index[language] >= len(languages_and_sections[language]):
            finished[language] = True
            continue

        heading_level, _heading, _contents = languages_and_sections[language][current_index[language]]
        current_heading_level = max(current_heading_level, heading_level)

    for language in languages:
        if finished[language]:
            row.append("")
            continue

        heading_level, heading, contents = languages_and_sections[language][current_index[language]]

        if heading_level == current_heading_level:
            row.append(
                get_report_for_section(heading_level, heading, contents)
            )
            current_index[language] += 1
        else:
            row.append("")

    if all(column == "" for column in row):
        current_heading_level = 0
    else:
        rows.append(row)

def format_datetime_numeric(date):
    return f"{format_date_numeric(date)}-at-{format_time_24h(date)}"


def format_date_numeric(date):
    return utc_string_to_aware_gmt_datetime(date).strftime("%Y-%m-%d")


def format_time_24h(date):
    return utc_string_to_aware_gmt_datetime(date).strftime("%H%M")


now = format_datetime_numeric(datetime.now(timezone.utc).isoformat())

Path(f"reports/{now}.html").write_text(report_template.render(rows=rows))

Path(f"index.html").write_text(index_template.render(reports=[
    (report.stem.replace("-", " "), f"{report}") for report in Path('reports').glob('*.html')
]))
