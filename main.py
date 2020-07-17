
import os
import time
from datetime import timedelta
import math
import numpy as np
import matplotlib.pyplot as plt
import xarray as xr
import pandas as pd
import folium
import webbrowser
from uploadgrib import *


from operator import itemgetter
import pickle
from shapely.geometry import Point,Polygon
from shapely import speedups

from flask import Flask, redirect, url_for,render_template, request , session , flash
from flask_sqlalchemy import SQLAlchemy


from calcul import add
from frouteur import frouteur

from polaires.polaires_imoca import *
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


#Depart : Latitude -43.6450  Longitude -59.4267
#Arrivee: Latitude -49.25  Longitude -5.17

latar=49.25
longar=-5.16666666

##partie serveur web


@app.route('/')
def index():
  return render_template('index.html')



@app.route('/resultat',methods = ['POST'])
def resultat():
  resultat1 = request.form                                    # dictionnaire avec les resultats de la requete
                                                              # resultat = request.args dans le cas d'une requete 'GET'
  latdep                 = resultat1['lat']
  longdep                = resultat1['long']

  frouteur (latdep,longdep,latar,longar)

 
  return render_template("map.html", total=add(latdep,longdep) , result=request.form)




















if __name__ == "__main__" :
    db.create_all()                 #creation de la base de donnees
    app.debug=True
    app.run(host='127.0.0.1', port=8080, debug=True)