from mongoengine import Document, StringField, DateField, ListField, EmbeddedDocument, EmbeddedDocumentField

class Reference(EmbeddedDocument):
    id = StringField(required=True)
    ref_author = StringField(required=True)
    ref_text = StringField(required=True)
    ref_article_title = StringField(required=True)
    citations = ListField(EmbeddedDocumentField('Citation'))
    syntactic_frequency = StringField(required=True)

class Citation(EmbeddedDocument):
    citation_section = StringField(required=True)
    citation_context = StringField(required=True)
    citation_text = StringField(required=True)

class Article(Document):
    doi = StringField(required=True)
    article_title = StringField(required=True)
    journal_title = StringField(required=True)
    publisher_name = StringField(required=True)
    publish_date = DateField(required=True)
    references = ListField(EmbeddedDocumentField(Reference))

# # Define the models
# class Place(Document):
#     title = StringField(required=True)
#     description = StringField(required=True)
#     image = StringField(required=True)
#     address = StringField(required=True)
#     creator = ObjectIdField(required=True)

# class User(Document):
#     name = StringField(required=True)
#     email = StringField(required=True)
#     password = StringField(required=True, min_length=6)
#     image = StringField(required=True)
#     places = ListField(ObjectIdField(required=True))