process_html_payload_schema = {
    "title": "ProcessHTML",
    "type": "object",
    "properties": {
        "content_type": {
            "type": "string"
        },
        "content": {
            "type": "string",
            "minLength": 1
        }
    },
    "required": ["content_type", "content"]
}
