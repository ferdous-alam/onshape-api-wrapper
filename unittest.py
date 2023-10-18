from src.onshape_api import OnshapeAPI
import unittest
import os

api_access = input("Enter your API access: ")
api_secret = input("Enter your API secret: ")

# example url from ABC dataset
url = "https://cad.onshape.com/documents/24a9baee35a3e7bd44af0404/w/376a01ff7426ab12a9682ffe/e/ec89d869e8682c5fa2c0d576"
        
class TestAPIwrapper(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.api = OnshapeAPI(api_access=api_access, api_secret=api_secret)
        if not os.path.exists('export'):
            os.makedirs('export')

    def test_export_stl(self):
        filename = 'export/test.stl'
        self.api.export_stl(url, filename=filename)
        self.assertTrue(os.path.exists(filename))

    def test_export_step(self):
        filename = 'export/test.step'
        self.api.export_stl(url, filename=filename)
        self.assertTrue(os.path.exists(filename))

    def test_version_id(self):
        filename = 'export/test.step'
        self.api.get_version(url)

    def test_features(self):
        self.api.get_features(url)



if __name__ == '__main__':
    unittest.main()
