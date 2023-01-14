import os
from flask import Flask, request
from mongoengine import connect
from mongoengine.fields import *
from mongoengine.errors import NotUniqueError
from flask_cors import CORS
from pubmed import open_article

from models import Article, Citation, Reference

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000"])

db = connect(
    db='Articles',
    username='Categorising_in_text_Citations',
    password='#Food123',
    host='mongodb+srv://cluster0.gkdshl2.mongodb.net/'
)

@app.route('/upload', methods=['POST'])
def upload():
    try:
        print("upload function")
        file = request.files['file']
        if file:
            filename = file.filename
            schema = open_article(file)
            try:
                article = Article(**schema)
                article.save()
                
            except NotUniqueError:
                # Handle the error
                print("Article with doi '{}' already exists".format(article.doi))

            except Exception as e:
                # Roll back the changes
                print(e)
            return 'File uploaded successfully'
        else:
            return 'No file found'
    except Exception as e:
        print("Error: ", e)
        print("Request: ", request)
        return 'An error occurred while uploading the file', 400

@app.route('/')
def article():
    session = db.start_session()
    
    # Start the session
    session.start_transaction()

    try:
        # Save the article
        article = Article(doi='10.7717/peerj-cs.421',
                        article_title='A systematic metadata harvesting workflow for analysing scientific networks',
                        journal_title='PeerJ Computer Science',
                        publisher_name='PeerJ Inc.',
                        publish_date='9-2-2021',
                        references=[])
        article.save(session=session)

        # Save the reference
        reference = Reference(id='ref-2',
                            ref_author='AlNoamany, Borghi',
                            ref_text='Al N oamany Y Borghi J A Towards computational reproducibility: researcher perspectives on the use and sharing of software Peer J Computer Science 2018 4 7317 e163 10.7717/peerj-cs.163',
                            ref_article_title='Towards computational reproducibility: researcher perspectives on the use and sharing of software',
                            citations=[Citation(citation_section='Introduction',
                                            citation_context='journals or a subject category. One such analysis is the identification of prominent authors (gurus).',
                                            citation_text='Python is used based on its popularity with researchers as per survey results by AlNoamany & Borghi (2018).')],
                            syntactic_frequency='1')
        article.references.append(reference)
        article.save(session=session)

        # Commit the changes
        session.commit_transaction()

        print("Successful..")

    except Exception as e:
        # Roll back the changes
        session.abort_transaction()
        print(e)

    # End the session
    session.end_session()

    return 'Success'

if __name__ == '__main__':
    app.run()

