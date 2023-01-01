from mongoengine import Document, StringField, DateField, ListField, EmbeddedDocumentField

from Models.Reference import Reference

# class Article(Document):
#     doi = StringField(required=True)
#     article_title = StringField(required=True)
#     #abstract = StringField(required=True)
#     journal_title = StringField(required=True)
#     publisher_name = StringField(required=True)
#     publish_date = DateField(required=True)
#     article_authors = ListField(StringField(required=True))
#     references = ListField(EmbeddedDocumentField(Reference))

class Article(Document):
    doi = StringField(required=True)
    article_title = StringField(required=True)
    journal_title = StringField(required=True)
    publisher_name = StringField(required=True)
    publish_date = DateField(required=True)
    references = ListField(EmbeddedDocumentField(Reference))

# article_schema = {
#     "validator": {
#         "$jsonSchema": {
#             "bsonType": "object",
#             "required": ["doi", "article_title", "abstract", "journal_title", "publisher_name", "publish_date", "article_authors"],
#             "properties": {
#                 "doi": {
#                     "bsonType": "string",
#                     "description": "must be a string and is required",
#                     "required": True
#                 },
#                 "article_title": {
#                     "bsonType": "string",
#                     "description": "must be a string and is required",
#                     "required": True
#                 },
#                 "abstract": {
#                     "bsonType": "string",
#                     "description": "must be a string and is required",
#                     "required": True
#                 },
#                 "journal_title": {
#                     "bsonType": "string",
#                     "description": "must be a string and is required",
#                     "required": True
#                 },
#                 "publisher_name": {
#                     "bsonType": "string",
#                     "description": "must be a string and is required",
#                     "required": True
#                 },
#                 "publish_date": {
#                     "bsonType": "string",
#                     "description": "must be a string and is required",
#                     "required": True
#                 },
#                 "article_authors": {
#                     "bsonType": "string",
#                     "description": "must be a string and is required",
#                     "required": True
#                 },
#             }
#         }
#     }
# }

# db.create_collection("articles", validator=article_schema)

