from mongoengine import EmbeddedDocument, StringField, ListField, IntField, FloatField, EmbeddedDocumentField

# class Reference(EmbeddedDocument):
#     id = StringField(required=True, primary_key=True)
#     ref_doi = StringField()
#     ref_author = StringField(required=True)
#     ref_text = StringField(required=True)
#     ref_article_title = StringField(required=True)
#     citations = ListField(EmbeddedDocumentField('Citation'))
#     syntactic_frequency = IntField(required=True)
#     polarity_score = FloatField(required=True)
#     intro_frequency = IntField(required=True)
#     method_frequency = IntField(required=True)
#     results_frequency = IntField(required=True)
#     discussion_frequency = IntField(required=True)
#     score = FloatField(required=True)
#     scoring_category = StringField(required=True)

class Reference(EmbeddedDocument):
    id = StringField(required=True)
    ref_author = StringField(required=True)
    ref_text = StringField(required=True)
    ref_article_title = StringField(required=True)
    citations = ListField(EmbeddedDocumentField('Citation'))
    syntactic_frequency = StringField(required=True)



# Reference_schema = {
#     "validator": {
#         "$jsonSchema": {
#             "bsonType": "object",
#             "properties": {
#                 "id": {
#                     "bsonType": "string",
#                     "description": "must be a string and is required",
#                     "required": True
#                 },
#                 "ref_author": {
#                     "bsonType": "string",
#                     "description": "must be a string and is required",
#                     "required": True
#                 },
#                 "ref_text": {
#                     "bsonType": "string",
#                     "description": "must be a string and is required",
#                     "required": True
#                 },
#                 "ref_text": {
#                     "bsonType": "string",
#                     "description": "must be a string and is required",
#                     "required": True
#                 },
#                 "ref_article_title": {
#                     "bsonType": "string",
#                     "description": "must be a string and is required",
#                     "required": True
#                 },
#                 "citation": {
#                     "type": "list",
#                     "properties": {
#                         "reference_id": {
#                             "bsonType": "string",
#                             "description": "must be a string and is required",
#                             "required": True
#                         },
#                         "citation_mark": {
#                             "bsonType": "string",
#                             "description": "must be a string and is required",
#                             "required": True
#                         },
#                         "citation_section": {
#                             "bsonType": "string",
#                             "description": "must be a string and is required",
#                             "required": True
#                         },
#                         "citation_context": {
#                             "bsonType": "string",
#                             "description": "must be a string and is required",
#                             "required": True
#                         },
#                         "citation_context": {
#                             "bsonType": "string",
#                             "description": "must be a string and is required",
#                             "required": True
#                         }
#                     }
#                 }
#             }

#         }
#     }
# }


