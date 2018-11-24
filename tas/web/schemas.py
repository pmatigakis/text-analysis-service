process_html_payload_schema = {
    "title": "ProcessHTML",
    "type": "object",
    "properties": {
        "content_type": {
            "type": "string"
        },
        "content": {
            "type": "object"
        }
    },
    "required": ["content_type", "content"]
}
