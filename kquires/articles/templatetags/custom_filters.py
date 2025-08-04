from django import template
import re
import uuid

register = template.Library()

@register.filter
def extract_h1(value):
    """
    Extracts all <h1> tags from the given HTML content,
    removes inline styles, converts them into <p> tags,
    and filters out empty or whitespace-only content.
    """
    if not value:
        return []

    # Match all <h1> tags and their content
    h1_tags = re.findall(r'<h[1-6][^>]*>(.*?)</h[1-6]>', value, re.IGNORECASE)

    cleaned = []
    for heading in h1_tags:
        # Remove the style attribute
        cleaned_heading = re.sub(r'style="[^"]*"', '', heading, flags=re.IGNORECASE)
        # Strip whitespace and check if the content is not empty or whitespace-only
        stripped_content = cleaned_heading.strip()
        if stripped_content and stripped_content != "&nbsp;":
            # Wrap valid content in a <p> tag
            cleaned.append(f"<p>🔹 {stripped_content}</p>")

    return cleaned


@register.filter
def extract_other_headings(value):
    """
    Extracts all <h2> to <h6> tags from the given HTML content,
    removes inline styles, converts them into <p> tags,
    and filters out empty or whitespace-only content.
    """
    if not value:
        return []

    # Match all <h2> to <h6> tags and their content
    other_tags = re.findall(r'<h[2-6][^>]*>(.*?)</h[2-6]>', value, re.IGNORECASE)

    cleaned = []
    for heading in other_tags:
        # Remove the style attribute
        cleaned_heading = re.sub(r'style="[^"]*"', '', heading, flags=re.IGNORECASE)
        # Strip whitespace and check if the content is not empty or whitespace-only
        stripped_content = cleaned_heading.strip()
        if stripped_content and stripped_content != "&nbsp;":
            # Wrap valid content in a <p> tag
            cleaned.append(f"<p>{stripped_content}</p>")

    return cleaned

@register.filter
def extract_headings(content):
    """
    Extract H1 and H2 headings from HTML content with unique IDs
    """
    if not content:
        return []

    # Regular expression to find H1 and H2 tags
    heading_pattern = re.compile(r'<h([12])([^>]*)>(.*?)</h\1>', re.IGNORECASE | re.DOTALL)

    processed_headings = []
    for match in heading_pattern.finditer(content):
        level, attrs, text = match.groups()

        # Generate unique ID
        unique_id = f'heading-{str(uuid.uuid4())[:8]}'

        # Check if an ID already exists in attributes
        id_match = re.search(r'id\s*=\s*[\'"]([^\'"]+)', attrs)
        if id_match:
            unique_id = id_match.group(1)

        processed_headings.append({
            'id': unique_id,
            'text': re.sub(r'<[^>]+>', '', text).strip(),  # Strip HTML tags
            'level': f'h{level}'
        })

    return processed_headings
