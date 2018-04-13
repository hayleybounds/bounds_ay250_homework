
from flask import Flask, render_template, request, url_for, redirect, flash
import flask
import pybtex.database as pb
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.debug = True
app.secret_key = 'Super Secret PW'
db=SQLAlchemy(app)

#TODO: somehow move at least some of this to another file?
class Citation(db.Model):
    __tablename__ = 'bibliography'
    id = db.Column(db.Integer, primary_key=True)
    ReferenceTag = db.Column(db.String)
    Collection = db.Column(db.String)
    #Adsnote = db.Column(db.String)
    #Adsurl = db.Column(db.String)
    Author = db.Column(db.String)
    #Date_Added = db.Column(db.Date)
    #Date_Modified = db.Column(db.Date)
    Journal = db.Column(db.String)
    Keywords = db.Column(db.String)
    #Month = db.Column(db.String)
    Pages = db.Column(db.String) #I think?
    Title = db.Column(db.String)
    Volume = db.Column(db.Integer)
    Year = db.Column(db.Integer)
    #Bdsk_File_1  = db.Column(db.String)
    
db.create_all()

@app.route("/")
@app.route("/home")
def home():
    return render_template('base.html', page_title="Home", message="Welcome! </p> this is my site")

@app.route('/query_database/', methods=['GET', 'POST'])
def query_db():
    if request.method == 'POST':
        query = request.form['query']
        #empty form submission doesn't return None, so don't check for that
        if query not in (""," "):
            result=db.engine.execute(query).fetchall()
            if len(result) > 0:
                display_query_results(x)
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
        if file not in (""," "):
            coll_name = request.form['collection_name']
            if coll_name not in (""," ",None):
                #read and convert to this database thing.
                x=pb.parse_bytes(file.read(), bib_format='bibtex')
                for k, entry in x.entries.items():
                    add_entry_to_db(k, entry, coll_name)
                return render_template('base.html', page_title= coll_name)
            else:
                return render_template('file_up.html',
                                       message = 'Please enter a valid collection name')
        else:
            return render_template('file_up.html', message = 'Please Choose a File')
    else:
        ## this is a normal GET request
        return render_template("file_up.html", page_title = 'Upload a File :)')

def display_query_results(results):
    fields = ['ReferenceTag','Collection', 'Title', 'Author','Journal', 'Keywords',
              'Pages', 'Volume', 'Year']
    for row in results:
        for field in fields:
            print(field)
            flash(field + ': ' + str(row[field]))
        flash('</br>')
    
    
def add_entry_to_db(key, entry, collection):
    keywords = {}
    for field in ['Title', 'Author','Journal', 'Keywords', 'Pages', 'Volume', 'Year']:
        if field in entry.fields:
            keywords[field] = entry.fields[field]
        else:
            keywords[field] = None
    db.session.add(Citation(**keywords, Collection = collection, ReferenceTag = key))
    db.session.commit()
    
if __name__ == "__main__":
    app.run()