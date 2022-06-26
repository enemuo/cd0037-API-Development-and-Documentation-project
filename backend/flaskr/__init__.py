import os
from unicodedata import category
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
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Methods', 'GET, POST, PATCH, DELETE, OPTIONS')
        return response
    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories', methods=['GET'])
    def get_categories():
        categories = Category.query.all()
        formatted_categories = [category.format() for category in categories]
        page = request.args.get('pages', 1, type=int)
        start = (page - 1) * 10
        end = start + 10
        return jsonify({
            'success': True,
            'categories': formatted_categories[start:end],
            'total_categories':len(formatted_categories)
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
    def paginate_questions(request, selection):
        page = request.args.get("page", 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE

        questions = [question.format() for question in selection]
        current_questions = questions[start:end]

        return current_questions

    @app.route("/questions")
    def retrieve_questions():
        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, selection)

        if len(current_questions) == 0:
            abort(404)

        return jsonify(
            {
                "success": True,
                "questions": current_questions,
                "current_category": category,
                "number_of_questions": len(Question.query.all()),
            }
        )
    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(question_id):
        try:
            question = Question.query.filter(Question.id == question_id).one_or_none()

            if question is None:
                abort(404)

            question.delete()
            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)

            return jsonify(
                {
                    "success": True,
                    "deleted": question_id,
                    "question": current_questions,
                    "number_of_questions": len(Question.query.all()),
                }
            )

        except:
            abort(422)
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
    def create_question():
        body = request.get_json()

        new_question = body.get("question", None)
        new_answer = body.get("answer", None)
        new_category = body.get("category", None)
        new_difficulty = body.get("difficulty", None)

        try:
            question = Question(question=new_question, category=new_category, difficulty=new_difficulty,answer=new_answer)
            question.insert()

            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)

            return jsonify(
                {
                    "success": True,
                    "created": question.id,
                    "questions": current_questions,
                    "number_of_questions": len(Question.query.all()),
                }
            )

        except:
            abort(422)
    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route("/questions/<int:question_id>", methods=["POST"])
    def search_question(question_id):

        body = request.get_json()

        try:
            question = Question.query.filter(Question.id == question_id).one_or_none()
            if question is None:
                abort(404)

            if "title" in body:
                question.id = int(body.get("title"))

            question.update()

            return jsonify({"success": True, "id": question.id})

        except:
            abort(400)
    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route("/categories")
    def retrieve_categories():
        selection = Category.query.order_by(Category.id).all()
        current_categories = paginate_questions(request, selection)

        if len(current_categories) == 0:
            abort(404)

        return jsonify(
            {
                "success": True,
                "categories": current_categories,
                "number_of_questions": len(Category.query.all()),
            }
        )
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
    @app.route("/questions/<int:question_category>", methods=["POST"])
    def search_random_question(question_category):

        body = request.get_json()
        random = random.randint(1, len(Category))
        try:
            question = Question.query.filter(question_category).one_or_none()

            if random in body:
                question.id = int(body.get(question))

            question.update()

            return jsonify({"success": True, "id": question.id})

        except:
            abort(400)
    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False, 
            "error": 404,
            "message": "Question or category Not found"
            }), 404

    @app.errorhandler(422)
    def not_processed(error):
        return jsonify({
            "success": False, 
            "error": 422,
            "message": "unprocessible"
            }), 422 

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False, 
            "error": 400,
            "message": "Bad Request"
            }), 400               
    return app

