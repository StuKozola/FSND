import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

# Pagination
QUESTIONS_PER_PAGE = 10


def paginate_questions(page, q_list):
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    questions = [q.format() for q in q_list]
    return questions[start:end]

# utility functions


def isempty_404(q):
    # abort if query q returns 0
    if len(q) == 0:
        abort(404)
    return False


def isempty_422(body, required_field):
    # abort if body of json required field is empty
    for f in required_field:
      if not (f in body):
        abort(422)
    return False


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    # # Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    cors = CORS(app, resource={r'/*': {'origins': '*'}})

    # Use the after_request decorator to set Access-Control-Allow
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PATCH,POST,DELETE,OPTIONS')
        return response

    # -------------------------------------------------------------------
    # endpoints
    # -------------------------------------------------------------------

    # Categories
    @app.route('/categories')
    def get_categories():
        categories = Category.query.order_by(Category.type).all()
        isempty_404(categories)
        return jsonify({
            'success': True,
            'categories': {c.id: c.type for c in categories}
        })

    # Questions endpoint with pagination
    # can be called with /questions or /questions?page=page_id
    @app.route('/questions')
    def get_questions():
        questions = Question.query.order_by(Question.id).all()
        question_page = paginate_questions(
            request.args.get('page', 1, type=int), questions)
        isempty_404(question_page)  # abort if empty

        categories = Category.query.order_by(Category.type).all()

        return jsonify({
            'questions': question_page,
            'total_questions': len(questions),
            'current_category': None,
            'categories': {c.id: c.type for c in categories},
            'success': True
        })

    # Endpoint to DELETE question using a question ID.
    @app.route('/questions/<question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            q = Question.query.get(question_id)
            q.delete()

            return jsonify({
                'deleted': question_id,
                'success': True
            })
        except:
            abort(422)

    # POST a new question, which will require the question
    # and answer text, category, and difficulty score.
    @app.route('/questions', methods=['POST'])
    def add_question():
        body = request.get_json()

        isempty_422(body, ['question', 'answer', 'category', 'difficulty'])
        try:
            question = body.get('question')
            answer = body.get('answer')
            category = body.get('category')
            difficulty = body.get('difficulty')

            q = Question(question=question, answer=answer,
                         category=category, difficulty=difficulty)
            q.insert()

            return jsonify({
                'created': q.id,
                'success': True
                })

        except:
            abort(422)

    # get questions based on a search term.
    # It should return any questions for whom the search term
    # is a substring of the question.
    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        try:
          term = request.get_json().get('searchTerm', None)
          questions = Question.query.filter(
            Question.question.ilike(f'%{term}%')).all()

          isempty_404(questions)

          return jsonify({
            'questions': [q.format() for q in questions],
            'total_questions': len(questions),
            'current_category': None,
            'success': True
            })

        except:
          abort(404)

    # Get questions based on category.
    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def get_questions_by_category(category_id):
        try:
            questions = Question.query.filter(
                Question.category == str(category_id)).all()

            isempty_404(questions)
            
            return jsonify({
                'questions': [q.format() for q in questions],
                'total_questions': len(questions),
                'current_category': category_id,
                'success': True
            })
        except:
            abort(404)

    # get questions to play the quiz.
    # This endpoint should take category and previous question parameters
    # and return a random questions within the given category,
    # if provided, and that is not one of the previous questions.
    @app.route('/quizzes', methods=['POST'])
    def quiz():
        body = request.get_json()
        isempty_422(body, ['quiz_category', 'previous_questions'])

        try:
            category = body.get('quiz_category')
            previous_questions = body.get('previous_questions')

            if category['type'] == 'click':
                question_pool = Question.query.filter(
                    Question.id.notin_((previous_questions))).all()
            else:
                question_pool = Question.query.filter_by(category=category['id']).filter(
                    Question.id.notin_((previous_questions))).all()

            if len(question_pool) > 0:
              index = random.randrange(0, len(question_pool))
              q = question_pool[index].format()
            else:
              q = None

            return jsonify({
                'question': q,
                'success': True
            })

        except:
            abort(422)

    # error handlers
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "Bad Request"
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "Not Found"
        }), 404

    @app.errorhandler(405)
    def method_not_alowed(error):
        return jsonify({
            "success": False,
            "error": 405,
            "message": "Method Not Allowed"
        }), 405

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "Unprocessable Entity"
        }), 422

    @app.errorhandler(500)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "Internal Server Error"
        }), 422

    return app