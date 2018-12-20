"""NOTE: Application Setup and Project Layout is copied from http://flask.pocoo.org/docs/1.0/tutorial/"""

import os

from flask import Flask, request, flash, redirect, make_response, jsonify, abort
from flask_restplus import Resource, Api, fields
from .LegalMation import XmlParser
from werkzeug.datastructures import FileStorage
from lxml import etree
from . import db

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'app-db.sqlite'),
    )
    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    api = Api(app, version='1.0', title='LegalMation XMLParser', description="Parses text from xml file")
    ns = api.namespace('documents', description="Uploaded XML documents.")

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db.init_app(app)
    
    # Fields for swagger
    document_api = api.model('Document', {
        'id': fields.Integer(readOnly=True, description='The document unique identifier'),
        'filename': fields.String(required=True, description='The document filename'),
        'plaintiff': fields.String(required=True, description='The extracted plantiff text'),
        'defendants': fields.String(required=True, description='The extracted defendants text')
    })
    
    upload_parser = api.parser()
    upload_parser.add_argument('file', location='files', type=FileStorage, required=True)
    
    ''' ROUTES '''
    
    @ns.route('/')
    class DocumentList(Resource):
        
        @ns.doc('list_documents')
        @ns.marshal_list_with(document_api)
        def get(self):
            '''List all documents'''
            
            all_documents = find_documents()
            return [dict(row) for row in all_documents]

    @ns.route('/<int:document_id>')
    @ns.response(404, 'Document not found')
    @ns.param('document_id', 'The document unique identifier')
    class Document(Resource):
        
        @ns.doc('get_document')
        @ns.marshal_with(document_api)
        def get(self, document_id):
            '''List one document by id'''
            
            document = find_document_by_id(document_id)
            if document is not None:
                return dict(document)
            else:
                api.abort(404, "Document {} doesn't exist".format(document_id))
    
    @ns.route('/upload')
    @ns.expect(upload_parser)
    @ns.response(400, 'Upload failure')
    class UploadDocument(Resource):
        
        @ns.doc('upload_document')
        @ns.marshal_with(document_api)
        def post(self):
            '''Upload an xml file'''
            
            if 'file' not in request.files:
                api.abort(400, 'No file part')
            
            file = request.files['file']
            
            if file:
                try:
                    lm_xml_parser = XmlParser(file)
                    # Parses the xml file and extracts its data
                    parsed_data = lm_xml_parser.extract()
                    
                    # Insert into database and get the newly created id
                    row_id = insert_document(file.filename, parsed_data['plaintiff'], parsed_data['defendants'])
                    
                    # Return the newly inserted document as json object
                    document = find_document_by_id(row_id)
                    return dict(document)
                except IOError:
                    abort(400, 'Invalid xml file.')
    
    return app

'''
    NOTE: We really shouldn't be putting sql queries here.
    But since the application is small, we will keep all database functions here.
    For larger scale applications, we should probably use some type of model library
        and move outside of main app file.
'''
def find_documents():
    """Find and return all document Row objects"""

    sql = "SELECT * FROM document"

    database = db.get_db()
    return database.execute(sql).fetchall()

def find_document_by_id(row_id):
    """Find and return one document Row object
    
    :param row_id: int id
    """
    sql = "SELECT * FROM document WHERE id = ?"

    database = db.get_db()
    return database.execute(sql, (row_id,)).fetchone()

def insert_document(filename, plaintiff, defendants):
    """Create a new document Row object and return its id
    
    :param filename: string filename
    :param plaintiff: string plaintiff data
    :param defendants: string defendants data
    """
    
    sql = "INSERT INTO document (filename, plaintiff, defendants) VALUES (?, ?, ?)"
    
    database = db.get_db()
    
    cursor = database.cursor()
    cursor.execute(sql, (filename, plaintiff, defendants))
    
    database.commit()
    last_row_id = cursor.lastrowid
    cursor.close()
    
    return last_row_id