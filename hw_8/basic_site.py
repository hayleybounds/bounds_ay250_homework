
from flask import Flask, render_template, request, url_for, redirect, flash
import flask
import pybtex.database as pb
from flask_sqlalchemy import SQLAlchemy
from config import Config
import numpy as np
from database import db, Citation
from sqlalchemy.exc import OperationalError

app = Flask(__name__)
app.config.from_object(Config)
with app.app_context():
    db.init_app(app)
    db.create_all()

@app.route("/")
@app.route("/home")
@app.route("/home/", methods=['GET', 'POST'])
def home():
    """Welcomes the user and tells them how many collections are in the database
    If post, clears the database."""
    if request.method == 'POST':  #clear the database if the button was pressed
        with app.app_context():
            db.drop_all()
            db.create_all()
        this_message = 'Database cleared. Upload a new file to get started!'
        
    elif Citation.query.first() is None:  #check for empty db
        this_message = 'You have no collections. Upload a file to get started!'
    else:  #get number of collections and names
        collections = \
            np.unique(Citation.query.with_entities(Citation.Collection).all())
        colls_w_sizes = \
            [s+' (%s entries)' %get_size_collection(s) for s in collections]
        this_message = ('You have %s collections, with names : ' % len(collections)) + \
                        ', '.join([s for s in colls_w_sizes]) 
            
    return render_template('home.html', page_title="Home",
                           message="Welcome! </p>This is a site for querying" +
                               "bibtex files </p>"+ this_message)


@app.route('/query_database/', methods=['GET', 'POST'])
def query_db():
    """Displays the form.html page with a form for querying. If POST, attempts
    to query the database and if the query provides results, displays them using
    message flashing."""
    if request.method == 'POST':
        query = request.form['query']
        #given a query, add the sql prefix stuff to it
        orig_query = query
        query = 'SELECT * FROM bibliography WHERE ' + query
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
            return render_template('form.html', page_title= 'Results for : ' + orig_query)
        else:
            return render_template('form.html', page_title= 'Query Database', 
                                   message='Invalid query. Please try again')
    else:  #if GET, display page
        return render_template("form.html", page_title = 'Query Database')
    
@app.route('/upload_file/', methods=['GET', 'POST'])
def upload_file():
    """Has a form to upload a file and provide a collection name. Tests
    that collection name + file were provided, then uses helper methods
    to add the bibtex file to the database"""
    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template('file_up.html', message = 'Please Choose a File')
        file = request.files['file']
        coll_name = request.form['collection_name']
        if coll_name not in (""," "):
            add_file_to_db(coll_name, file)
            return render_template('base.html', page_title='Added collection: ' + coll_name)
        else:
            return render_template('file_up.html',
                                   message = 'Please enter a valid collection name')
    else:
        ## this is a normal GET request
        return render_template("file_up.html", page_title = 'Upload a File :)')

def display_query_results(results):
    """flashes a message for each of the fields to be displayed. These are then
    displayed by the template as bullets"""
    fields = ['ReferenceTag','Collection', 'Title', 'Author','Journal', 'Keywords',
              'Pages', 'Volume', 'Year']
    for row in results:
        for field in fields:
            if field == 'Year':  #for the final row, and a break
                flash(field + ': ' + str(row[field]) + '</br></br>')
            else:
                flash(field + ': ' + str(row[field]))
                
def add_file_to_db(coll_name, file):
    """uses pybtex to parse the file, then iterates through entries and adds them
    to the database"""
    parsed_file=pb.parse_bytes(file.read(), bib_format='bibtex')
    for k, entry in parsed_file.entries.items():
        add_entry_to_db(k, entry, coll_name)
                
def add_entry_to_db(key, entry, collection):
    """creates a keywords dictionary that is used to pass arguments to Citation,
    so that I don't have to pass each field individually. Deals with the oddities
    of pybtex's author storage and creates a list of authors"""
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
    with app.app_context():
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