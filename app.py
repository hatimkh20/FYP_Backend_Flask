from flask import Flask
from mongoengine import connect
from mongoengine.fields import *
from mongoengine.document import Document

app = Flask(__name__)

connect(
    db='database',
    username='Categorising_in_text_Citations',
    password='#Food123',
    host='mongodb+srv://cluster0.gkdshl2.mongodb.net/'
)

class User(Document):
    name = StringField(required=True)
    email = EmailField()

@app.route('/users')
def user():
    return "User found."

@app.route('/')
def create_user():
    user = User(name='Hatim', email='john@example.com')
    user.save()
    return "Successful"

if __name__ == '__main__':
    app.run()



# client = pymongo.MongoClient(CONNECTION_STRING)
# db = client.get_database('flask_mongodb_atlas')
# user_collection = pymongo.collection.Collection(db, 'user_collection')



# @app.route('/')
# # ‘/’ URL is bound with hello_world() function.
# def hello_world():
#     db.collection.insert_one({"name": "aiman"})
#     print(db)
#     return "Successful"


