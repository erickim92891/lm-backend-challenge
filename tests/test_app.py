import os

import pytest

def test_no_route(client):
    """
    GIVEN a client
    WHEN the client accesses a non-valid route
    THEN a 404 error is returned
    """
    rv = client.get('/invalid-route')
    assert rv.status_code == 404

def test_document_post(client):
    """
    GIVEN a client
    WHEN the client makes a POST rqeuest to '/documents/1'
    THEN a 405 error is returned
    """
    rv = client.post('/documents/1')
    assert rv.status_code == 405

def test_documents_post(client):
    """
    GIVEN a client
    WHEN the client makes a POST rqeuest to '/documents/'
    THEN a 405 error is returned
    """
    rv = client.post('/documents/')
    assert rv.status_code == 405

def test_document_with_no_data(client):
    """
    GIVEN a client
    WHEN the client makes a GET request to '/documents/1'
    THEN a 404 error is returned
    """
    rv = client.get('/documents/1')
    assert rv.status_code == 404

def test_documents_with_no_data(client):
    """
    GIVEN a client
    WHEN the client makes a GET request to '/'
    THEN an empty json list is returned
    """
    rv = client.get('/documents/')
    assert rv.status_code == 200
    assert rv.get_json() == []

def test_document_with_data(client):
    """
    GIVEN a client
    AND a xml file is uploaded
    WHEN the client makes a GET request to '/documents/1'
    THEN a one json object is returned
    """
    upload_file(client, 'A.xml')
    rv = client.get('/documents/1')
    assert rv.status_code == 200
    assert rv.get_json()

def test_document_with_wrong_id(client):
    """
    GIVEN a client
    AND a xml file is uploaded
    WHEN the client makes a GET request to '/documents/2'
    THEN a 404 error is returned
    """
    upload_file(client, 'A.xml')
    rv = client.get('/documents/2')
    assert rv.status_code == 404

def test_documents_with_data(client):
    """
    GIVEN a client
    AND a xml file is uploaded
    WHEN the client makes a GET request to '/documents/'
    THEN a json list with at least one entry is returned
    """
    upload_file(client, 'A.xml')
    rv = client.get('/documents/')
    assert rv.status_code == 200
    assert len(rv.get_json()) > 0

def test_upload_with_no_file(client):
    """
    GIVEN a client
    WHEN the client makes a POST request to '/documents/upload'
    THEN a 400 error code is returned
    AND a `No file part` text is returned
    """
    rv = client.post('/documents/upload')
    assert rv.status_code == 400
    assert b'No file part' in rv.data

def test_upload_with_invalid_file(client):
    """
    GIVEN a client
    WHEN the client makes a POST request to '/documents/upload' with 'A.txt' file
    THEN a 400 error code is returned
    AND a `Invalid xml file.` text is returned
    """
    rv = upload_file(client, 'A.txt')
    assert rv.status_code == 400
    assert b'Invalid xml file.' in rv.data

def test_upload_with_valid_file(client):
    """
    GIVEN a client
    WHEN the client makes a POST request to '/documents/upload' with 'A.xml' file
    THEN a non-empty json object is returned
    AND the `defendants` value equals 'HILL-ROM COMPANY, INC., an Indiana ) corporation; and DOES 1 through 100, inclusive, )'
    AND the `plaintiff` value equals 'ANGELO ANGELES, an individual,' 
    """
    rv = upload_file(client, 'A.xml')
    assert rv.status_code == 200
    
    data = rv.get_json()
    
    assert type(data) == type({}) and len(data) > 0
    assert data['defendants'] == 'HILL-ROM COMPANY, INC., an Indiana ) corporation; and DOES 1 through 100, inclusive, )'
    assert data['plaintiff'] == 'ANGELO ANGELES, an individual,'

def upload_file(client, file_name):
    """Uploads a xml file by requesting a POST request to '/documents/uploads'"""
    path = os.path.join(os.path.dirname(__file__), file_name)
    files = {'file': (open(path, 'rb'), file_name)}
    rv = client.post('/documents/upload', data=files)
    
    return rv