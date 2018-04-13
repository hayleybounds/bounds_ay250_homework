import os
import unittest
from basic_site import app

class FlaskrTestCase(unittest.TestCase):

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
    
    def test_query_submission(self):
        """tests invalid queries and queries to empty databases"""
        assert b'Results for' in self.submit_query('SELECT * from bibliography').data
        assert b'No results' in self.submit_query('SELECT * from bibliography').data
        assert b'Invalid' in self.submit_query('').data
        assert b'Invalid' in self.submit_query(' ').data        

if __name__ == '__main__':
    unittest.main()