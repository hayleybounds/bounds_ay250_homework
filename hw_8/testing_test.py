import os
import unittest
from basic_site import app
from io import BytesIO

class FlaskTestCase(unittest.TestCase):

    def setUp(self):
        #self.db_fd, flaskr.app.config['DATABASE'] = tempfile.mkstemp()
        app.testing = True
        self.app = app.test_client()
        #with flaskr.app.app_context():
        #    flaskr.init_db()

    def tearDown(self):
        #os.close(self.db_fd)
        #os.unlink(flaskr.app.config['DATABASE'])
        pass
    
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
    
    def upload_file(self, coll_name, filename, filecontent=b'SOME CONTENT'):
        """helper method to mimic the user choosing a file and collection name"""
        data = {
            'collection_name': coll_name,
            'file': (BytesIO(filecontent), filename)
        }

        return self.app.post('/upload_file/', buffered=True,
                         content_type='multipart/form-data',
                         data=data)
        
    def test_file_upload(self):
        rv = self.upload_file('ex', 'hw_8_data/homework_8_refs.bib')
        assert rv.status_code == 200
        assert b'ex' in rv.data
    
    def test_query_submission(self):
        """tests invalid queries and queries to empty databases"""
        assert b'Results for' in self.submit_query('SELECT * from bibliography').data
        assert b'z' in self.submit_query('SELECT * from bibliography').data
        assert b'Invalid' in self.submit_query('').data
        assert b'Invalid' in self.submit_query(' ').data
    
    def test_bad_file_upload(self):
        """tests failure to provide collection names or to choose a file"""
        rv = self.upload_file('', 'hw_8_data/homework_8_refs.bib')
        assert b'enter a valid collection name' in rv.data
        data = {'collection_name': 'ex' }

        rv = self.app.post('/upload_file/', buffered=True,
                         content_type='multipart/form-data',
                         data=data)
        assert b'Please Choose a File' in rv.data
    #def test_collection_size(self):
    #    """make sure collection size works"""
    
    

if __name__ == '__main__':
    unittest.main()