from flask import Flask
from flask_pymongo import pymongo

app = Flask(__name__)

CONNECTION_STRING = "mongodb+srv://Categorising_in_text_Citations:#Food123@cluster0.gkdshl2.mongodb.net/?retryWrites=true&w=majority"
client = pymongo.MongoClient(CONNECTION_STRING)
db = client.get_database('flask_mongodb_atlas')
user_collection = pymongo.collection.Collection(db, 'user_collection')

@app.route('/')
# ‘/’ URL is bound with hello_world() function.
def hello_world():
    db.collection.insert_one({"name": "John"})
    print(db)
    return "Successful"

if __name__ == '__main__':
    app.run()