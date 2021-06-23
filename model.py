import os
import sys

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL') or \
    'sqlite:///' + os.path.join(basedir, 'banners.db')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True  # mute warnings
app.secret_key = os.getenv('SECRET_KEY')


db = SQLAlchemy(app)

#626x417

class Banner(db.Model):

    '''
    CREATE TABLE "banner" (
        "id"    INTEGER,
        "name"  TEXT,
        "image_url1"    TEXT,
        "image_url2"    TEXT,
        "text"  TEXT,
        "background"    TEXT,
        "price" TEXT,
        "discount"  TEXT,
        "background_transparency"   TEXT,
        "remove_background" TEXT,
        PRIMARY KEY("id")
    )
    '''

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))  # for caching banners
    image_url1 = db.Column(db.String(100))  # from dropdown
    image_url2 = db.Column(db.String(500))  # image URL
    text = db.Column(db.String(500))
    price = db.Column(db.String(500))
    discount = db.Column(db.String(500))
    background = db.Column(db.String(500))
    background_transparency = db.Column(db.Boolean)
    remove_background = db.Column(db.Boolean)

    def __init__(self, banner):
        self.name = banner.name
        self.image_url1 = banner.image1
        self.image_url2 = banner.image2
        self.text = banner.text
        self.price = banner.price
        self.discount = banner.discount
        self.background = banner.background
        self.background_transparency = banner.background_transparency
        self.remove_background = banner.remove_background

    def __repr__(self):
        return '<Banner %r>' % self.name


if __name__ == '__main__':

    # TODOs: use a migration tool like Alembic
    # make User model if more people are interested

    if len(sys.argv) > 1 and '-r' in sys.argv[1]:

        print('You are about to recreate the DB, all data will be lost!')
        confirm = input('Are you sure? ')

        if str(confirm).lower()[0] == 'y':
            db.drop_all()
            print('Running drop_all')
        else:
            print('Skipping drop_all')

    print('Running create_all')
    db.create_all()
