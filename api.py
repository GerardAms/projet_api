from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from sqlalchemy.exc import IntegrityError
import os

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + \
    os.path.join(basedir, "db_centre.sqlite")

db = SQLAlchemy(app)
ma = Marshmallow(app)

# Définition de la classe Article
class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), unique=True, nullable=False)
    desc = db.Column(db.String(200), nullable=False)
    prix = db.Column(db.Float, nullable=False)
    quantite = db.Column(db.Integer, nullable=False)
    categorie_id = db.Column(db.Integer, db.ForeignKey('categorie.id'), nullable=False)

    def __init__(self, nom, desc, prix, quantite, categorie_id):
        self.nom = nom
        self.desc = desc
        self.prix = prix
        self.quantite = quantite
        self.categorie_id = categorie_id

# Définition de la classe Catégorie
class Categorie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), unique=True, nullable=False)
    desc = db.Column(db.String(200), nullable=False)
    articles = db.relationship('Article', backref='categorie', lazy=True)

    def __init__(self, nom, desc):
        self.nom = nom
        self.desc = desc

# Définition du schéma de sérialisation pour Article
class ArticleSchema(ma.Schema):
    class Meta:
        fields = ('id', 'nom', 'desc', 'prix', 'quantite', 'categorie_id')

article_schema = ArticleSchema()
articles_schema = ArticleSchema(many=True)

with app.app_context():
    db.create_all()
    print('Database created')

# Endpoint pour consulter tous les articles
@app.route('/articles', methods=['GET'])
def get_articles():
    all_articles = Article.query.all()
    result = articles_schema.dump(all_articles)
    return jsonify(result), 200

# Endpoint pour consulter un article par son id
@app.route('/articles/<id>', methods=['GET'])
def get_article(id):
    article = Article.query.get(id)
    return article_schema.jsonify(article)

# Endpoint pour ajouter un article
@app.route('/articles', methods=['POST'])
def add_article():
    nom = request.json['nom']
    desc = request.json['desc']
    prix = request.json['prix']
    quantite = request.json['quantite']
    categorie_id = request.json['categorie_id']

    new_article = Article(nom, desc, prix, quantite, categorie_id)
    db.session.add(new_article)
    try:
        db.session.commit()
        return jsonify({'message': 'Article ajouté avec succès.'}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({'message': 'Erreur: cet article existe déjà.'}), 409


if __name__ == "__main__":
    app.run(debug=True)
