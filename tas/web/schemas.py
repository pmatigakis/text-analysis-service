process_html_payload_schema = {
    "title": "ProcessHTML",
    "type": "object",
    "properties": {
        "url": {
            "type": "string"
        },
        "html": {
            "type": "string"
        },
        "headers": {
            "type": "object"
        }
    },
    "required": ["url", "html", "headers"]
}
