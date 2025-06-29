import unittest
from app import create_app, db
from app.models import DataLog


class DataTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_log_entry_creation(self):
        log = DataLog(source='test', data={'key': 'value'}, data_hash='abc')
        db.session.add(log)
        db.session.commit()
        self.assertEqual(DataLog.query.count(), 1)
        self.assertEqual(DataLog.query.first().source, 'test')

if __name__ == '__main__':
    unittest.main()
