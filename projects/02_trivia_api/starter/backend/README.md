# Full Stack Trivia API Backend

## Getting Started

### Installing Dependencies

#### Python 3.7

Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)

#### Virtual Enviornment

We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organaized. Instructions for setting up a virual enviornment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

#### PIP Dependencies

Once you have your virtual environment setup and running, install dependencies by naviging to the `/backend` directory and running:

```bash
pip install -r requirements.txt
```

This will install all of the required packages we selected within the `requirements.txt` file.

##### Key Dependencies

- [Flask](http://flask.pocoo.org/)  is a lightweight backend microservices framework. Flask is required to handle requests and responses.

- [SQLAlchemy](https://www.sqlalchemy.org/) is the Python SQL toolkit and ORM we'll use handle the lightweight sqlite database. You'll primarily work in app.py and can reference models.py. 

- [Flask-CORS](https://flask-cors.readthedocs.io/en/latest/#) is the extension we'll use to handle cross origin requests from our frontend server. 

## Database Setup
With Postgres running, restore a database using the trivia.psql file provided. From the backend folder in terminal run:
```bash
psql trivia < trivia.psql
```

## Running the server

From within the `backend` directory first ensure you are working using your created virtual environment.

To run the server, execute:

```bash
export FLASK_APP=flaskr
export FLASK_ENV=development
flask run
```

Setting the `FLASK_ENV` variable to `development` will detect file changes and restart the server automatically.

Setting the `FLASK_APP` variable to `flaskr` directs flask to use the `flaskr` directory and the `__init__.py` file to find the application. 

## Testing
To run the tests, run
```
dropdb trivia_test
createdb trivia_test
psql trivia_test < trivia.psql
python test_flaskr.py
```

## Tasks

One note before you delve into your tasks: for each endpoint you are expected to define the endpoint and response data. The frontend will be a plentiful resource because it is set up to expect certain endpoints and response data formats already. You should feel free to specify endpoints in your own way; if you do so, make sure to update the frontend or you will get some unexpected behavior. 

1. [x] Use Flask-CORS to enable cross-domain requests and set response headers. 
2. [x] Create an endpoint to handle GET requests for questions, including pagination (every 10 questions). This endpoint should return a list of questions, number of total questions, current category, categories. 
3. [x] Create an endpoint to handle GET requests for all available categories. 
4. [x] Create an endpoint to DELETE question using a question ID. 
5. [x] Create an endpoint to POST a new question, which will require the question and answer text, category, and difficulty score. 
6. [x] Create a POST endpoint to get questions based on category. 
7. [x] Create a POST endpoint to get questions based on a search term. It should return any questions for whom the search term is a substring of the question. 
8. [x] Create a POST endpoint to get questions to play the quiz. This endpoint should take category and previous question parameters and return a random questions within the given category, if provided, and that is not one of the previous questions. 
9. [x] Create error handlers for all expected errors including 400, 404, 422 and 500. 

## API
### Available Endpoints
- `GET '/categories'`
- `GET '/questions?page={page_id}'`
- `DELETE '/questions/{question_id}'`
- `POST '/questions`
- `POST '/questions/search'`
- `GET '/categories/{category_id}/questions'`
- `POST '/quizzes'`

### Error Messages
- 400: Bad Request
- 404: Not Found
- 405: Method Not Allowed
- 422: Unprocessable Entity
- 500: Internal Server Error

Error format:
```
{
    "success": False,
    "error": <Erorr ID>,
    "message": <Error Message>
}
```

### `GET '/categories'`
- Fetches a dictionary of categories in which the keys are the ids and the value is the corresponding string of the category
- _Request Arguments:_ None
- _Returns:_ An object with a single key, categories, that contains a object of id: category_string key:value pairs.

Example: 
`curl http://localhost:5000/categories`
Response:
```
{
  "categories": {
    "1": "Science", 
    "2": "Art", 
    "3": "Geography", 
    "4": "History", 
    "5": "Entertainment", 
    "6": "Sports"
  }, 
  "success": true
}
```
### `GET '/questions?page={page_number:integer}'`
- Fetches a dictionary of categories, current category, and a list of questions.  If page does note exist ir returns error message with status code 404
- _Request Arguments:_ optional page_number
- _Returns:_ An object with keys categories, current_category, and questions.  Categories contains a object of id: category_string key:value pairs.  Questions return a object of key:value pairs id, category, difficulty, question, and answer.
- Error code returned for invalid page number is 404
Example:
`curl http://localhost:5000/questions` or `curl http://localhost:5000/questions?page=1`
Response:
```
{
  "categories": {
    "1": "Science", 
    "2": "Art", 
    "3": "Geography", 
    "4": "History", 
    "5": "Entertainment", 
    "6": "Sports"
  }, 
  "current_category": null, 
  "questions": [
    {
      "answer": "Apollo 13", 
      "category": 5, 
      "difficulty": 4, 
      "id": 2, 
      "question": "What movie earned Tom Hanks his third straight Oscar nomination, in 1996?"
    }, 
    {
      "answer": "Tom Cruise", 
      "category": 5, 
      "difficulty": 4, 
      "id": 4, 
      "question": "What actor did author Anne Rice first denounce, then praise in the role of her beloved Lestat?"
    }, 
    {
      "answer": "Maya Angelou", 
      "category": 4, 
      "difficulty": 2, 
      "id": 5, 
      "question": "Whose autobiography is entitled 'I Know Why the Caged Bird Sings'?"
    }, 
    {
      "answer": "Edward Scissorhands", 
      "category": 5, 
      "difficulty": 3, 
      "id": 6, 
      "question": "What was the title of the 1990 fantasy directed by Tim Burton about a young man with multi-bladed appendages?"
    }, 
    {
      "answer": "Muhammad Ali", 
      "category": 4, 
      "difficulty": 1, 
      "id": 9, 
      "question": "What boxer's original name is Cassius Clay?"
    }, 
    {
      "answer": "Brazil", 
      "category": 6, 
      "difficulty": 3, 
      "id": 10, 
      "question": "Which is the only team to play in every soccer World Cup tournament?"
    }, 
    {
      "answer": "Uruguay", 
      "category": 6, 
      "difficulty": 4, 
      "id": 11, 
      "question": "Which country won the first ever soccer World Cup in 1930?"
    }, 
    {
      "answer": "George Washington Carver", 
      "category": 4, 
      "difficulty": 2, 
      "id": 12, 
      "question": "Who invented Peanut Butter?"
    }, 
    {
      "answer": "Lake Victoria", 
      "category": 3, 
      "difficulty": 2, 
      "id": 13, 
      "question": "What is the largest lake in Africa?"
    }, 
    {
      "answer": "The Palace of Versailles", 
      "category": 3, 
      "difficulty": 3, 
      "id": 14, 
      "question": "In which royal palace would you find the Hall of Mirrors?"
    }
  ], 
  "sucess": true, 
  "total questions": 19
}
```

### `DELETE '/questions/{question_id}'`
- Delete a question from the questions inventory give question_id (integer)
- _Request Arguments:_ question_id
- _Returns:_ An object with keys:values of deleted:question_id, succes:True
- Error code returned for invalid question_id is 422

Example:
`curl -X DELETE http://localhost:5000/questions/5`

Response:
```
{
  "deleted": "5", 
  "success": true
}
```

### `POST '/questions`
- Add a new question and answer set
- _Request Arguments:_ None
- _Request Body:_ json object with fields defining question, answer, catergory, and difficulty
- _Returns:_ An object with keys:values of created: question_id, succes:True
- Error code returned for invalid question_id is 422

Example:

`curl --request POST -H "Content-Type: application/json" -d '{"question": "What is the answer to the universe","answer":"42","difficulty": "1","category": "5"}' http://localhost:5000/questions`

Response:

```
{
  "created": 24, 
  "success": true
}
```
### `POST '/questions/search'`
- Search for a question based upon search term.
- _Request Arguments:_ None
- _Request Body:_ json object with fields defining search term
- _Returns:_ An object with keys:values of questions: list of matching questions, total_questions: number of questions found, current_category: None, success: true if found
- Error code returned for invalid search query is 404

Example:
`curl --request POST -H "Content-Type: application/json" -d '{"searchTerm":"medicine"}' http://localhost:5000/questions/search`

Response:
```
{
  "current_category": null, 
  "questions": [
    {
      "answer": "Blood", 
      "category": 1, 
      "difficulty": 4, 
      "id": 22, 
      "question": "Hematology is a branch of medicine involving the study of what?"
    }
  ], 
  "success": true, 
  "total_questions": 1
}
```
### `GET '/categories/{category_id}/questions'`
- Get the questions associated to a category
- _Request Arguments:_ category_id
- _Returns:_ A json object with keys:values of questions: questions in category, total_questions: count of returned questions, current_category: the current category_id, success: trud if found a result
- Error code returned for invalid category_id is 422

Example:

`curl http://localhost:5000/categories/6/questions`

Response:
```
{
  "current_category": 6, 
  "questions": [
    {
      "answer": "Brazil", 
      "category": 6, 
      "difficulty": 3, 
      "id": 10, 
      "question": "Which is the only team to play in every soccer World Cup tournament?"
    }, 
    {
      "answer": "Uruguay", 
      "category": 6, 
      "difficulty": 4, 
      "id": 11, 
      "question": "Which country won the first ever soccer World Cup in 1930?"
    }
  ], 
  "success": true, 
  "total_questions": 2
}
```
### `POST '/quizzes'`
- Get random questions remaining (play the quiz)
- _Request Arguments:_ none
- _Request Body:_ json object with fields defining quiz categry and previous questions
- _Returns:_ An object with keys:values of question: randomized question not yet seen, success: true if question found

- Error code returned for invalid question is 422 

Example:
`curl --request POST -H "Content-Type: application/json" -d '{"previous_questions":[],"quiz_category":{"type":"Sports","id":6}}' http://localhost:5000/quizzes`

Response:

```
{
  "question": {
    "answer": "Brazil", 
    "category": 6, 
    "difficulty": 3, 
    "id": 10, 
    "question": "Which is the only team to play in every soccer World Cup tournament?"
  }, 
  "success": true
}
```