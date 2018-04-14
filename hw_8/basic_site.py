
from flask import Flask, render_template, request, url_for, redirect, flash
import flask
import pybtex.database as pb
from flask_sqlalchemy import SQLAlchemy
from config import Config
import numpy as np
from sqlalchemy.exc import OperationalError

app = Flask(__name__)
app.config.from_object(Config)
db=SQLAlchemy(app)

#TODO: somehow move at least some of this to another file?
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
    
db.create_all()

@app.route("/")
@app.route("/home")
def home():
    """Welcomes the user and tells them how many collections are in the database."""
    if Citation.query.first() is None: #check for empty db
        this_message = 'You have no collections. Upload a file to get started!'
    else: #get number of collections and names
        collections = np.unique(Citation.query.with_entities(Citation.Collection).all())
        colls_w_sizes = [s+' (%s entries)' %get_size_collection(s) for s in collections]
        this_message = ('You have %s collections, with names : ' % len(collections)) + \
                        ', '.join([s for s in colls_w_sizes]) 
    
    return render_template('base.html', page_title="Home",
                           message="Welcome! </p>This is a site for querying bibtex files </p>"+
                                   this_message)

@app.route('/query_database/', methods=['GET', 'POST'])
def query_db():
    if request.method == 'POST':
        query = request.form['query']
        #empty form submission doesn't return None, so don't check for that
        if query not in (""," "):
            try:
                result=db.engine.execute(query).fetchall()
            except OperationalError:
                return render_template('form.html', page_title= 'Query Database', 
                                   message='Invalid query. Please try again.')
            if len(result) > 0:
                display_query_results(result)
            else:
                flash('No results to display :(')
            return render_template('form.html', page_title= 'Results for : ' + query)
        else:
            return render_template('form.html', page_title= 'Query Database', 
                                   message='Invalid query. Please try again')
    else:
        ## this is a normal GET request
        return render_template("form.html", page_title = 'Query a Database :)')
    
@app.route('/upload_file/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template('file_up.html', message = 'Please Choose a File')
        file = request.files['file']
        coll_name = request.form['collection_name']
        if coll_name not in (""," "):
            #read and convert to this database thing.
            x=pb.parse_bytes(file.read(), bib_format='bibtex')
            for k, entry in x.entries.items():
                add_entry_to_db(k, entry, coll_name)
            return render_template('base.html', page_title= coll_name)
        else:
            return render_template('file_up.html',
                                   message = 'Please enter a valid collection name')
    else:
        ## this is a normal GET request
        return render_template("file_up.html", page_title = 'Upload a File :)')

def display_query_results(results):
    fields = ['ReferenceTag','Collection', 'Title', 'Author','Journal', 'Keywords',
              'Pages', 'Volume', 'Year']
    for row in results:
        for field in fields:
            if field == 'Year':
                flash(field + ': ' + str(row[field]) + '</br></br>')
            else:
                flash(field + ': ' + str(row[field]))
    
def add_entry_to_db(key, entry, collection):
    keywords = {}
    for field in ['Title', 'Journal', 'Keywords', 'Pages', 'Volume', 'Year']:
        if field in entry.fields:
            keywords[field] = format_btex_fields(entry.fields[field])
        else:
            keywords[field] = None
    #handle author separately because its stored differently
    if 'Author' in entry.persons:
        author_list = [format_btex_fields(str(auth)) for auth in entry.persons['Author']]
        keywords['Author'] = ', '.join(author_list)
    else:
        keywords['Author'] = None
    db.session.add(Citation(**keywords, Collection = collection, ReferenceTag = key))
    db.session.commit()
    
def format_btex_fields(string):
    """helper method to remove odd formatting from btex files"""
    string = string.replace('{','')
    string = string.replace('}','')
    return string

def get_size_collection(collection):
    """helper method to get the number of entries in a collection"""
    return len(Citation.query.filter(Citation.Collection == collection).all())
    
if __name__ == "__main__":
    app.run()