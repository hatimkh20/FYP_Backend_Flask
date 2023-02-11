import os
from flask import Flask, request, jsonify
from mongoengine import connect
from mongoengine.fields import *
from mongoengine.errors import NotUniqueError, DoesNotExist
from flask_cors import CORS
from modules.pubmed import open_article
from models.models import Article

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
        file = request.files.get('file')
        if not file:
            return jsonify({"error": "No file found"}), 400

        if not file.filename.endswith(('json')):
            return jsonify({"error": "Invalid file type"}), 400

        file_path = os.path.join(os.getcwd(), file.filename)
        file.save(file_path)
        print("File saved to directory")
        schema = open_article(file_path)
        print("Schema return")
        os.remove(file_path)
        print("file removed from directory")

        try:
            article = Article(**schema)
            article.save()
            print("saved in DB")
            return schema, 201

        except NotUniqueError:
            # Handle the error
            print("Article with doi '{}' already exists".format(article.doi))
            return jsonify({"error": "Article with doi '{}' already exists".format(article.doi)}), 400

        except Exception as e:
            # Roll back the changes
            print(e)
            return jsonify({"error": str(e)}), 500

    except Exception as e:
        print("Error: ", e)
        return jsonify({"error": str(e)}), 500


@app.route("/search", methods=["GET"])
def search():
    try:
        query = request.args.get("query")
        if not query:
            return jsonify({"error": "query parameter is missing"}), 400
        articles = Article.objects.search_text(query).limit(10).to_json()
        
        # if articles.count() == 0:
        #     return jsonify({"error": "No articles found"}), 404
        return articles, 200, { 'Content-Type': 'application/json' }
    except DoesNotExist as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run()
