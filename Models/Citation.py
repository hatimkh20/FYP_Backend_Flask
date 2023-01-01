from mongoengine import EmbeddedDocument, StringField

# class Citation(EmbeddedDocument):
#     #reference_id = StringField(required=True)
#     citation_mark = StringField(required=True)
#     citation_section = StringField(required=True)
#     citation_context = StringField(required=True)
#     citation_text = StringField(required=True)

class Citation(EmbeddedDocument):
    citation_section = StringField(required=True)
    citation_context = StringField(required=True)
    citation_text = StringField(required=True)