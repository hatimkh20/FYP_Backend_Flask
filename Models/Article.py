import pymongo

CONNECTION_STRING = "mongodb+srv://Categorising_in_text_Citations:#Food123@cluster0.gkdshl2.mongodb.net/?retryWrites=truew=majority"
client = pymongo.MongoClient(CONNECTION_STRING)
db = client.get_database('articles')

article_schema = {
    "validator": {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["doi", "article_title", "abstract", "journal_title", "publisher_name", "publish_date", "article_authors"],
            "properties": {
                "doi": {
                    "bsonType": "string",
                    "description": "must be a string and is required",
                    "required": True
                },
                "article_title": {
                    "bsonType": "string",
                    "description": "must be a string and is required",
                    "required": True
                },
                "abstract": {
                    "bsonType": "string",
                    "description": "must be a string and is required",
                    "required": True
                },
                "journal_title": {
                    "bsonType": "string",
                    "description": "must be a string and is required",
                    "required": True
                },
                "publisher_name": {
                    "bsonType": "string",
                    "description": "must be a string and is required",
                    "required": True
                },
                "publish_date": {
                    "bsonType": "string",
                    "description": "must be a string and is required",
                    "required": True
                },
                "article_authors": {
                    "bsonType": "string",
                    "description": "must be a string and is required",
                    "required": True
                },
            }
        }
    }
}

db.create_collection("articles", validator=article_schema)
