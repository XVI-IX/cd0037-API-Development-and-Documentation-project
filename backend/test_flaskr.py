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
        self.new_question = {
            "question": "new_question",
            "answer": "answer",
            "category": 1,
            "difficulty": 2
        }
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

        # self.app = create_app() 
        # self.new_question = {
        #     "question": "new_question",
        #     "answer": "answer",
        #     "category": 1,
        #     "difficulty": 2
        # }
        self.fail_question = {
            "question": "",
            "answer": "",
            "category": None,
            "difficulty": None
        }
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["categories"])
        self.assertTrue(data["total_categories"])

    def test_404_get_categories(self):
        res = self.client().get("/categories?page=100")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "404: Page not Found")

    def test_get_questions(self):
        res = self.client().get("/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["categories"])
        self.assertTrue(data["questions"])
        self.assertTrue(data["total_questions"])
        self.assertEqual(data["current_category"], None)

    def test_404_get_questions(self):
        res = self.client().get("/questions?page=1000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "404: Page not Found")

    def test_delete_question(self):
        res = self.client().delete("/questions/1")
        data = json.loads(res.data)
        question = Question.query.filter(Question.id == 1)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["deleted"], 1)
    
    def test_404_delete_question(self):
        res = self.client().delete("/questions/1")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "404: Page not Found")

    def test_new_question(self):
        res = self.client().post("/questions", json=self.new_question)
        data = json.loads(res.data)
        # question = Question.query.filter_by(Question.id == q_id)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["created"])

    def test_422_new_question_fail(self):
        res = self.client().post("/questions", json=self.fail_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'],
         "422: Request could not be processed")
    
    def test_questions_by_cat(self):
        res = self.client().get("/categories/2/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        # self.assertEqual(data["category_id"], 2)
        self.assertTrue(data["category"])
        self.assertTrue(data["total_questions"])
        self.assertTrue(data["questions"])

    def test_404_questions_by_cat(self):
        res = self.client().get("/categories/2/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "404: Page not Found")

    def test_get_quiz(self):
        requestData = {
            "previous_questions": [],
            "quiz_category": { "id": 1 }
        }

        res = self.client().post("/quizzes", json=requestData)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["question"])

    def test_404_get_quiz(self):
        requestData = {
            "previous_questions": [],
            "quiz_category": {"id": 0}
        }
        res = self.client().post("/quizzes", json=requestData)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertTrue(data["message"], "404: Page not Found")



# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
