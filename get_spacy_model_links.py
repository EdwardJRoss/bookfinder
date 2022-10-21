#!/usr/bin/env python
import json
import urllib.request
from typing import List


def get_spacy_model_links() -> List[str]:
    url = "https://api.github.com/repos/explosion/spacy-models/releases"
    headers = {"Accept": "application/vnd.github+json"}
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read())
        links = [
            asset["browser_download_url"]
            for release in data
            for asset in release["assets"]
        ]
    return links


def spacy_model_links_to_html(links: List[str]) -> str:
    html = ["<!DOCTYPE html><html><body>"]
    for link in links:
        html.append(f'<a href="{link}">{link.split("/")[-1]}</a><br/>')
    html.append("</body></html>")
    return "\n".join(html)


if __name__ == "__main__":
    links = get_spacy_model_links()
    html = spacy_model_links_to_html(links)
    with open("spacy_model_links.html", "w") as f:
        f.write(html)
