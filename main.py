from flask import Flask, redirect, url_for,render_template, request , session , flash
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy
from calcul import add

# commentaire ajoute pour test


app = Flask(__name__)


app.secret_key="Hello"
app.permanent_session_lifetime = timedelta(days=1)     # minutes=10

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] =False
db = SQLAlchemy(app)

class user(db.Model):                                              # creation du modele de base de donnée
    id     = db.Column(db.Integer, primary_key=True)
    nom    = db.Column(db.String(100))
    prenom = db.Column(db.String(100))






@app.route('/')
def index():
  return render_template('index.html')



@app.route('/resultat',methods = ['POST'])
def resultat():
  resultat1 = request.form                                    # dictionnaire avec les resultats de la requete
                                                              # resultat = request.args dans le cas d'une requete 'GET'
  lat                 = resultat1['lat']
  long                = resultat1['long']
  return render_template("map.html", total=add(lat,long) , result=request.form)




















if __name__ == "__main__" :
    db.create_all()                 #creation de la base de donnees
    app.debug=True
    app.run(host='127.0.0.1', port=8080, debug=True)