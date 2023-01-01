from flask import Flask
from mongoengine import connect, Document, Q
from mongoengine.errors import NotUniqueError, ValidationError
from mongoengine.fields import *

from models import Article, Citation, Reference

app = Flask(__name__)

db = connect(
    db='Articles',
    username='Categorising_in_text_Citations',
    password='#Food123',
    host='mongodb+srv://cluster0.gkdshl2.mongodb.net/'
)

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


# @app.route('/createuser')
# def create():
#     # Start a session
#     session = db.start_session()

#     # Define the transaction
#     with session.start_transaction():
#         # Create the user
#         user = User(name='John Smith',
#                     email='john@example.com',
#                     password='password',
#                     image='https://example.com/john.jpg',
#                     places=[])
#         try:
#             user.save()
#             print("User saved...")
#         except (NotUniqueError, ValidationError) as e:
#             # Handle errors
#             session.abort_transaction()
#             print(e)
#             raise e

#         # Create the place
#         place = Place(title='Eiffel Tower',
#                       description='Iconic tower in Paris',
#                       image='https://example.com/eiffel-tower.jpg',
#                       address='Champ de Mars, 5 Avenue Anatole France, 75007 Paris, France',
#                     #   location={'lat': 48.8584, 'lng': 2.2945},
#                       creator=user.id)
#         try:
#             place.save()
#             print("Place saved...")
#         except (NotUniqueError, ValidationError) as e:
#             # Handle errors
#             session.abort_transaction()
#             print(e)
#             raise e

#         # Update the user's places field
#         user.update(push__places=place.id)

#     # End the session
#     session.end_session()

#     return 'Success'


# client = pymongo.MongoClient(CONNECTION_STRING)
# db = client.get_database('flask_mongodb_atlas')
# user_collection = pymongo.collection.Collection(db, 'user_collection')



# @app.route('/')
# # ‘/’ URL is bound with hello_world() function.
# def hello_world():
#     db.collection.insert_one({"name": "aiman"})
#     print(db)
#     return "Successful"


