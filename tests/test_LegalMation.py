"""Unit Test for LegalMation.XmlParser"""

import os

import pytest
from app import LegalMation
from werkzeug.datastructures import FileStorage
from lxml import etree

VALID_XML_FILE = os.path.join(os.path.dirname(__file__), 'A.xml')
INVALID_TXT_FILE = os.path.join(os.path.dirname(__file__), 'A.txt')

""" FIXTURES """
@pytest.fixture
def xml_file():
    """Fixture for exposing a xml FileStorage object to pytest functions"""
    
    with open(VALID_XML_FILE, 'rb') as fp:
        file = FileStorage(fp)
        yield file

@pytest.fixture
def invalid_txt_file():
    """Fixture for exposing a non-xml FileStorage object to pytest functions"""
    
    with open(INVALID_TXT_FILE, 'rb') as fp:
        file = FileStorage(fp)
        yield file

@pytest.fixture
def xml_parser(xml_file):
    """Fixture for exposing LegalMation.XmlParser object to pytest functions"""
    
    with open(VALID_XML_FILE, 'rb') as fp:
        file = FileStorage(fp)
        xml_parser = LegalMation.XmlParser(file)
        yield xml_parser

""" PUBLIC """
def test_xml_parser_missing_xml_file_argument():
    """
    GIVEN a LegalMation.XmlParser
    WHEN a new XmlParser is created with no arguments
    THEN a TypeError is raised
    """
    with pytest.raises(TypeError):
        LegalMation.XmlParser()

def test_xml_parser_invalid_file_storage_argument():
    """
    GIVEN a LegalMation.XmlParser
    WHEN a new XmlParser is created with a non FileStorage object
    THEN a TypeError is raised
    """
    with pytest.raises(TypeError):
        LegalMation.XmlParser(12345)

def test_xml_parser_non_xml_file_extension(invalid_txt_file):
    """
    GIVEN a LegalMation.XmlParser
    AND an invalid text file
    WHEN a new XmlParser is created with the invalid text file
    THEN an IOError is raised
    """
    with pytest.raises(IOError):
        LegalMation.XmlParser(invalid_txt_file)

def test_xml_parser_valid_xml_file(xml_file):
    """
    GIVEN a LegalMation.XmlParser
    AND a valid xml file
    WHEN a new XmlParser is created with the xml file
    THEN no exception is raised
    """
    LegalMation.XmlParser(xml_file)

def test_xml_parser_default_namespace(xml_parser):
    """
    GIVEN a LegalMation.XmlParser object
    THEN the default namespace is set to 'http://www.abbyy.com/FineReader_xml/FineReader10-schema-v1.xml'
    """
    assert xml_parser.namespace == 'http://www.abbyy.com/FineReader_xml/FineReader10-schema-v1.xml'

def test_xml_parser_custom_namespace(xml_file):
    """
    GIVEN a LegalMation.XmlParser
    AND a valid xml file
    WHEN a new XmlParser is created with the xml file
    AND the namespace argument is set to 'HELLO WORLD'
    THEN the namespace is equal to 'HELLO WORLD'
    """
    parser = LegalMation.XmlParser(xml_file, xml_namespace='HELLO WORLD')
    assert parser.namespace == 'HELLO WORLD'

def test_xml_parser_extract(xml_parser):
    """
    GIVEN a LegalMation.XmlParser object
    WHEN the extract method is called
    THEN a non-empty dictionary is returned
    """
    dictionary = xml_parser.extract()
    assert type(dictionary) == type({}) and len(dictionary.keys()) > 0

def test_xml_parser_get_parsed_texts_before_extract(xml_parser):
    """
    GIVEN a LegalMation.XmlParser object
    WHEN the get_parsed_texts method is called
    THEN an empty dictionary is returned
    """
    parsed_texts = xml_parser.get_parsed_texts()
    assert type(parsed_texts) == type({}) and len(parsed_texts.keys()) == 0

def test_xml_parser_get_parsed_texts_after_extract(xml_parser):
    """
    GIVEN a LegalMation.XmlParser object
    WHEN the extract method is called
    AND the get_parsed_texts method is called
    THEN a non-empty dictionary is returned
    """
    xml_parser.extract()
    parsed_texts = xml_parser.get_parsed_texts()
    assert type(parsed_texts) == type({}) and len(parsed_texts.keys()) > 0

def test_xml_parser_extract_plaintiff(xml_parser):
    """
    GIVEN a LegalMation.XmlParser object
    WHEN the extract method is called
    THEN the `plaintiff` value equals 'ANGELO ANGELES, an individual,' 
    """
    dictionary = xml_parser.extract()
    assert dictionary['plaintiff'] == 'ANGELO ANGELES, an individual,'

def test_xml_parser_extract_defendants(xml_parser):
    """
    GIVEN a LegalMation.XmlParser object
    WHEN the extract method is called
    THEN the `defendants` value equals 'HILL-ROM COMPANY, INC., an Indiana ) corporation; and DOES 1 through 100, inclusive, )' 
    """
    dictionary = xml_parser.extract()
    assert dictionary['defendants'] == 'HILL-ROM COMPANY, INC., an Indiana ) corporation; and DOES 1 through 100, inclusive, )'

def test_xml_parser_get_parsed_plaintiffs_after_extract(xml_parser):
    """
    GIVEN a LegalMation.XmlParser object
    WHEN the extract method is called
    AND the get_parsed_texts method is called
    THEN the `plaintiff` value equals 'ANGELO ANGELES, an individual,' 
    """
    xml_parser.extract()
    parsed_texts = xml_parser.get_parsed_texts()
    assert parsed_texts['plaintiff'] == 'ANGELO ANGELES, an individual,'

def test_xml_parser_get_parsed_defendants_after_extract(xml_parser):
    """
    GIVEN a LegalMation.XmlParser object
    WHEN the extract method is called
    AND the get_parsed_texts method is called
    THEN the `defendants` value equals 'HILL-ROM COMPANY, INC., an Indiana ) corporation; and DOES 1 through 100, inclusive, )'
    """
    xml_parser.extract()
    parsed_texts = xml_parser.get_parsed_texts()
    assert parsed_texts['defendants'] == 'HILL-ROM COMPANY, INC., an Indiana ) corporation; and DOES 1 through 100, inclusive, )'