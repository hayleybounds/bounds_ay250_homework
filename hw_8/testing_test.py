import os
import unittest
from basic_site import app, db, Citation, add_file_to_db
from io import BytesIO
from flask_sqlalchemy import SQLAlchemy

class FlaskTestCase(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        with app.app_context():
            db.drop_all()
            db.create_all()
    
    def test_home_page(self):
        rv = self.app.get('/')
        assert b'Welcome!' in rv.data
    
    def submit_query(self, query):
        #helper function to test querying
        return self.app.post('/query_database/', data=dict(
            query=query
        ), follow_redirects=True)
    
    def test_query_page(self):
        rv = self.app.get('/query_database/')
        assert b'name="query"' in rv.data
    
    def test_upload_file_page(self):
        rv = self.app.get('/upload_file/')
        
        assert b'Choose file to upload' in rv.data
        assert b'Upload a File' in rv.data
    
    def upload_file(self, coll_name, file, filename):
        """helper method to mimic the user choosing a file and collection name"""
        data = {
            'collection_name': coll_name,
            'file': (file, filename)
        }

        return self.app.post('/upload_file/', buffered=True,
                         content_type='multipart/form-data',
                         data=data)
        
    def test_file_upload(self):
        rv = self.upload_file('ex', open('hw_8/hw_8_data/homework_8_refs.bib','rb'),
                              'hw_8/hw_8_data/homework_8_refs.bib')
        assert rv.status_code == 200
        assert b'ex' in rv.data
        with app.app_context():
            assert len(Citation.query.all()) > 0
    
    def test_query_submission(self):
        """tests invalid queries and queries to empty databases"""
        assert b':(' in self.submit_query('Year < 1930').data
        assert b'Invalid' in self.submit_query('').data
        assert b'Invalid' in self.submit_query(' ').data
    
    def test_bad_file_upload(self):
        """tests failure to provide collection names or to choose a file"""
        rv = self.upload_file('',open('hw_8/hw_8_data/homework_8_refs.bib','rb'),
                              'hw_8/hw_8_data/homework_8_refs.bib')
        assert b'enter a valid collection name' in rv.data        
        data = {'collection_name': 'ex' }

        rv = self.app.post('/upload_file/', buffered=True,
                         content_type='multipart/form-data',
                         data=data)
        assert b'Please Choose a File' in rv.data

    def test_homepage_text(self):
        """test that the homepage properly displays collection info"""
        rv = self.app.get('/home/')
        assert b'no collections' in rv.data
    
    def test_homepage_text_not_empty(self):
        #then add collections and test that it shows them and entries
        add_file_to_db('ex', open('hw_8/hw_8_data/homework_8_refs.bib','rb'))
        add_file_to_db('ex2', open('hw_8/hw_8_data/homework_8_refs.bib','rb'))
        rv = self.app.get('/home/')
        assert b'ex (46 entries)' in rv.data
        assert b'ex2 (46 entries)' in rv.data
        
    def test_real_query(self):
        add_file_to_db('ex', open('hw_8/hw_8_data/homework_8_refs.bib','rb'))
        rv = self.submit_query('Author LIKE "%Dean%"')
        assert b'Dean' in rv.data
        assert b'Reddenings of Cepheids' in rv.data

if __name__ == '__main__':
    unittest.main()