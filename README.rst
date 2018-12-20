LegalMation Backend Coding Challenge
======

RESTful backend API to ingest xml file, process, and output results.

Install
-------

Clone Repo::

    # clone the repository
    git clone https://github.com/erickim92891/lm-backend-challenge
    cd lm-backend-challenge

Create a virtualenv and activate it::

    python3 -m venv venv
    . venv/bin/activate

Or on Windows cmd::

    py -3 -m venv venv
    venv\Scripts\activate.bat

Setup & Install Dependencies::

    pip install -e .

Run
---

Initialize Database::
    
    flask init-db

Start Server::

    export FLASK_APP=app
    export FLASK_ENV=development
    flask run

Or on Windows cmd::

    set FLASK_APP=app
    set FLASK_ENV=development
    flask run

Open http://127.0.0.1:5000 in a browser to view Swagger JSON API documentation


Test
----

::

    pip install -e '.[test]'
    pytest -v

Run with coverage report::

    coverage run -m pytest
    coverage report
    coverage html  # open htmlcov/index.html in a browser


API
----

Find all documents::

    curl -i -X GET http://127.0.0.1:5000/documents/

Find a document by id::
    
    # Replace <int:id> with an integer
    curl -i -X GET http://127.0.0.1:5000/documents/<int:id>                

Upload a document::
    
    # Replace <path_to_file> with the absolute filepath of the xml document
    curl -i -X POST -F file=@<path_to_file> http://127.0.0.1:5000/documents/upload
