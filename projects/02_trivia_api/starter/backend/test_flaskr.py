import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('postgres:postgres@localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    # test for enpoints and errors
    def test_get_categories(self):
        result = self.client().get('/categories')
        self.assertEqual(result.status_code, 200)

        data = json.loads(result.data)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['categories']))
    
    def test_get_categories_not_found(self):
        result = self.client().get('/categories/-1')
        self.assertEqual(result.status_code, 404)

        data = json.loads(result.data)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not Found')

    def test_get_questions(self):
        result = self.client().get('/questions')
        self.assertEqual(result.status_code, 200)

        data = json.loads(result.data)
        self.assertEqual(data['success'], True)
        self.assertIsNotNone(data['total_questions'])
        self.assertTrue(len(data['categories']))
        self.assertIsNotNone(data['questions'])

    def test_get_questions_page_2(self):
        result = self.client().get('/questions?page=2')
        self.assertEqual(result.status_code, 200)

        data = json.loads(result.data)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['categories']))
        self.assertTrue(len(data['questions']))

    def test_get_questions_page_not_found(self):
        result = self.client().get('/questions?page=9999')
        self.assertEqual(result.status_code, 404)
        
        data = json.loads(result.data)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not Found')

    def test_quesions_method_not_allowed(self):
        result = self.client().get('/questions/1')
        self.assertEqual(result.status_code, 405)

        data = json.loads(result.data)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Method Not Allowed')
    
    def test_delete_question(self):
        q = Question(question='Test Question', answer='Test Answer',difficulty=1, category=1)
        q.insert()

        result = self.client().delete(f'/questions/{q.id}')
        self.assertEqual(result.status_code, 200)

        data = json.loads(result.data)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], str(q.id))

        # make sure database item is removed
        self.assertEqual(Question.query.filter(Question.id == q.id).one_or_none(), None)

    def test_delete_question_unprocessable(self):
        result = self.client().delete('/questions/-1')
        self.assertEqual(result.status_code, 422)

        data = json.loads(result.data)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable Entity') 
   
    def test_add_question(self):
        q = {
            'question': 'Adding a question',
            'answer': 'Question is added!',
            'difficulty': 1,
            'category': 1
        }

        tot_q = len(Question.query.all())

        result = self.client().post('/questions', json=q)
        self.assertEqual(result.status_code, 200)

        data = json.loads(result.data)
        self.assertEqual(data['success'], True)
        self.assertIsNotNone(data['created'])

        # verify database is updated
        self.assertEqual(tot_q + 1, len(Question.query.all()))

    def test_add_missing_question_field(self):
        q = {
            'question': 'Adding a question',
            'answer': 'Question is added!',
            'difficulty': 1,
        }

        tot_q = len(Question.query.all())

        result = self.client().post('/questions', json=q)
        self.assertEqual(result.status_code, 422)

        data = json.loads(result.data)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable Entity') 

    def test_search_question(self):
        result = self.client().post('/questions/search', json={'searchTerm': 'Wh'})
        self.assertEqual(result.status_code, 200)

        data = json.loads(result.data)
        self.assertEqual(data['success'], True)
        self.assertIsNotNone(data['questions'])
        self.assertIsNotNone(data['total_questions'])

    def test_search_question_not_found(self):
        result = self.client().post('/questions/search', json={'searchTerm': '@#$@#'})
        self.assertEqual(result.status_code, 404)

        data = json.loads(result.data)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not Found') 

    def test_get_questions_by_category(self):
        result = self.client().get('/categories/6/questions')
        self.assertEqual(result.status_code, 200)

        data = json.loads(result.data)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['current_category'])

    def test_get_questions_by_category_not_found(self):
        result = self.client().get('/categories/9999/questions')
        self.assertEqual(result.status_code, 404)

        data = json.loads(result.data)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not Found') 

    def test_quiz(self):
        quiz = {'previous_questions': [], 'quiz_category': {'type': 'Sports', 'id': 6} }

        result = self.client().post('quizzes', json=quiz)
        self.assertEqual(result.status_code, 200)

        data = json.loads(result.data)
        self.assertEqual(data['success'], True)

    def test_quiz_uprocessable(self):
        quiz = {'previous_questions': [], 'quiz_category': []}

        result = self.client().post('quizzes', json=quiz)
        self.assertEqual(result.status_code, 422)

        data = json.loads(result.data)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable Entity')

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()