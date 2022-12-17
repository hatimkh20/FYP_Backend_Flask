from flask import Flask
from flask_pymongo import PyMongo
 
# Flask constructor takes the name of
# current module (__name__) as argument.
app = Flask(__name__)

app.config['MONGO_URI'] = 'mongodb+srv://Categorising_in_text_Citations:#Food123@cluster0.gkdshl2.mongodb.net/?retryWrites=true&w=majority'

mongo = PyMongo(app)
# The route() function of the Flask class is a decorator,
# which tells the application which URL should call
# the associated function.
@app.route('/')
# ‘/’ URL is bound with hello_world() function.
def hello_world():
    
    return mongo.db.list_collection_names
 
# main driver function
if __name__ == '__main__':
 
    # run() method of Flask class runs the application
    # on the local development server.
    app.run()