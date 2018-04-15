
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Citation(db.Model):
    __tablename__ = 'bibliography'
    id = db.Column(db.Integer, primary_key=True)
    ReferenceTag = db.Column(db.String)
    Collection = db.Column(db.String)
    Author = db.Column(db.String)
    Journal = db.Column(db.String)
    Keywords = db.Column(db.String)
    Pages = db.Column(db.String)
    Title = db.Column(db.String)
    Volume = db.Column(db.Integer)
    Year = db.Column(db.Integer)