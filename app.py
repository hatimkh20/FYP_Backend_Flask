import json
import os
os.environ['CUDA_VISIBLE_DEVICES'] = ''
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

        if not file.filename.endswith(('xml')):
            return jsonify({"error": "Invalid file type"}), 400

        file_path = os.path.join(os.getcwd(), file.filename)
        file.save(file_path)
        print("File saved to directory")
        schema = open_article(file_path)
        print("Schema return")
        os.remove(file_path)
        print("File removed from directory")

        if isinstance(schema, str):
            # schema is a DOI, return it
            return jsonify({"doi": schema}), 200
        else:
            # schema is an article object, save it and return its DOI
            article = Article(**schema)
            existing_article = Article.objects(doi=article.doi).first()
            if existing_article:
                return jsonify({"doi": existing_article.doi}), 200
            else:
                article.save()
                article.reload()
                if not article.doi:
                    return jsonify({"error": "Failed to save article"}), 500
                return jsonify({"doi": article.doi}), 201

    except NotUniqueError:
        # Handle the error
        print("Article with doi '{}' already exists".format(article.doi))
        return jsonify({"error": "Article with doi '{}' already exists".format(article.doi)}), 400

    except Exception as e:
        # Roll back the changes
        print(e)
        return jsonify({"error": str(e)}), 500

@app.route("/search", methods=["GET"])
def search():
    try:
        query = request.args.get("query")
        if not query:
            return jsonify({"error": "query parameter is missing"}), 400
        articles = Article.objects.search_text(query).limit(20)
        reduced_articles = []
        for article in articles:
            article = json.loads(article.to_json())
            reduced_articles.append({
                "id": article["_id"]["$oid"],
                "title": article["article_title"],
                "doi": article["doi"]
    })
        return jsonify(reduced_articles), 200, { 'Content-Type': 'application/json' }
    except DoesNotExist as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/article", methods=["GET"])
def get_article():
    try:
        article_id = request.args.get("doi")
        if not article_id:
            return jsonify({"error": "article id is missing"}), 400
        article = Article.objects.get(doi=article_id)
        return article.to_json(), 200, { 'Content-Type': 'application/json' }
    except DoesNotExist as e:
        return jsonify({"error": "Article not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run()
