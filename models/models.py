from mongoengine import Document, StringField, FloatField, ListField, IntField, EmbeddedDocument, EmbeddedDocumentField


class Reference(EmbeddedDocument):
    id = StringField(required=True, primary_key=True)
    ref_doi = StringField()
    ref_author = StringField(required=True)
    ref_text = StringField(required=True)
    ref_article_title = StringField()
    citations = ListField(EmbeddedDocumentField('Citation'))
    is_referenced_count = IntField()
    syntactic_frequency = IntField(required=True)
    syntactic_score = FloatField()
    polarity_score = FloatField(required=True)
    Introduction = IntField(required=True)
    Method = IntField(required=True)
    Results = IntField(required=True)
    Discussion = IntField(required=True)
    score = FloatField(required=True)
    scoring_category = StringField(required=True)

class Citation(EmbeddedDocument):
    reference_id = StringField(required=True)
    citation_mark = StringField()
    citation_section = StringField()
    citation_text = StringField()
    sentiment = FloatField()
    multi_citance = IntField()

class Article(Document):
    doi = StringField(required=True, pk=True, unique=True)
    article_title = StringField(required=True)
    abstract = StringField()
    journal_title = StringField()
    publisher_name = StringField()
    publish_date = StringField()
    article_authors = ListField(StringField(required=True))
    references = ListField(EmbeddedDocumentField(Reference))