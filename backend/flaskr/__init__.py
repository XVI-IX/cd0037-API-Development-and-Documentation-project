import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app)

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type, Authorization, true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET, PUT, POST, DELETE, OPTIONS"
        )
        response.headers.add(
            "Access-Control-Allow-Origin", "*"
        )

        return response

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route("/categories", methods=["GET"])
    def get_categories():

        """
        * Endpoint to fetch categories in the api ordered by their ids
        * Arguments: Accepts no arguments
        * Return: Returns a json object containing the success status, categories and total number of categories in the api.
        * Sample request: `curl http://127.0.0.1:5000/categories`
        """

        page = request.args.get("page", 1, type=int)
        categories = Category.query.order_by(Category.id).all()
        formatted_categories = [category.format() for category in categories]

        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE

        if len(formatted_categories) is not None:
            return jsonify({
                "success": True,
                "categories": formatted_categories[start:end],
                "total_categories": len(formatted_categories)
            })


    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route("/questions", methods=["GET"])
    def get_questions():
        page = request.args.get("page", 1, type=int)
        questions = Question.query.order_by(Question.id).all()
        categories = Category.query.order_by(Category.id).all()
        formatted_categories = [category.format() for category in categories]
        # current_category = [question.category for question in questions]


        formatted_questions = [question.format() for question in questions]

        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE

        if questions is not None:

            return jsonify({
                "success": True,
                "questions": formatted_questions[start:end],
                "total_questions": len(questions),
                "current_category": None,
                "categories": formatted_categories[start:end]

            })
    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.


    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(question_id):

        question = Question.query.filter(Question.id==question_id)
        
        question.delete()

        return jsonify({

            "question":None,
            "success": True,
            "deleted": question_id,

        })
    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route("/questions", methods=["POST"])
    def new_question():
        question_body = request.get_json()

        if any(question_body) != "":
            new_question = question_body.get("question")
            new_answer = question_body.get("answer")
            new_category = question_body.get("category")
            new_difficult = question_body.get("difficulty")

            question = Question(
                question=new_question, answer=new_answer,
                category=new_category, difficulty=new_difficult)
        else:
            abort(422)
        try:
            question.insert()
        except Exception as e:
            print(e)
            abort(500)

        return jsonify({
            "success": True,
            "created": str(question.id),
        })

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route("/questions/search", methods=["POST"])
    def search_question():

        search = request.get_json().get("searchTerm", None)

        questions = Question.query.filter(Question.question.ilike(f"%{search}%")).all()
        formatted_questions = [question.format() for question in questions]

        return jsonify({
            "success": True,
            "total_questions": len(questions),
            "questions": formatted_questions,
        })
    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route("/categories/<int:cat_id>/questions", methods=["GET"])
    def questions_by_cat(cat_id):
        category = Category.query.get(cat_id)
        category = category.format()["type"]

        if category is not None:
            questions = Question.query.filter_by(category=cat_id).all()
            formatted_questions = [question.format() for question in questions]

            return jsonify({
                "success": True,
                # "category_id": cat_id,
                "total_questions": len(formatted_questions),
                "category": str(category),
                "questions": formatted_questions,
            })
        else:
            abort(404)
    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route("/quiz", methods=["POST"])
    def get_quiz():
        data = request.get_json()

        previous_questions = data.get("previous_questions")
        category = data.get("quiz_category")

        if (previous_questions is None) or (category is None):
            abort(400)

        if category["id"] == 0:
            questions = Question.query.filter(
                Question.id.notin_(previous_questions)
            ).order_by(
                Question.id
            ).all()
        else:
            questions = Question.query.filter_by(
                category=category.get("id")
                ).filter(
                    Question.id.notin_(previous_questions)
                ).all()

        if not questions:
            abort(404)

        # formatted_questions = [question for question in questions if question.id not in previous_questions]
        quiz = random.choice(questions).format()

        return jsonify({
            "success": True,
            "question": quiz
        })
    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "message": "404: Page not Found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "sucess": True,
            "message": "422: Request could not be processed"
        }), 422

    return app

