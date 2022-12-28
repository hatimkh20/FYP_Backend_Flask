
Reference_schema = {
    "validator": {
        "$jsonSchema": {
            "bsonType": "object",
            "properties": {
                "id": {
                    "bsonType": "string",
                    "description": "must be a string and is required",
                    "required": True
                },
                "ref_author": {
                    "bsonType": "string",
                    "description": "must be a string and is required",
                    "required": True
                },
                "ref_text": {
                    "bsonType": "string",
                    "description": "must be a string and is required",
                    "required": True
                },
                "ref_text": {
                    "bsonType": "string",
                    "description": "must be a string and is required",
                    "required": True
                },
                "ref_article_title": {
                    "bsonType": "string",
                    "description": "must be a string and is required",
                    "required": True
                },
                "citation": {
                    "type": "list",
                    "properties": {
                        "reference_id": {
                            "bsonType": "string",
                            "description": "must be a string and is required",
                            "required": True
                        },
                        "citation_mark": {
                            "bsonType": "string",
                            "description": "must be a string and is required",
                            "required": True
                        },
                        "citation_section": {
                            "bsonType": "string",
                            "description": "must be a string and is required",
                            "required": True
                        },
                        "citation_context": {
                            "bsonType": "string",
                            "description": "must be a string and is required",
                            "required": True
                        },
                        "citation_context": {
                            "bsonType": "string",
                            "description": "must be a string and is required",
                            "required": True
                        }
                    }
                }
            }

        }
    }
}
