def text_to_html(text):
    if not text:
        return ""

    paragraphs = text.split("\n\n")

    html = ""

    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if paragraph:
            html += f"<p>{paragraph}</p>\n"

    return html