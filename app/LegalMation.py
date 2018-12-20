import os
import re

from flask import request
from lxml import etree
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage

class XmlParser:
    """A parser to extract plaintiff and defendant texts from a Legalmation xml file
    
    :param xml_file: <werkzeug.datastructures.FileStorage> object
    :param xml_namespace: namespace prefix used in xml document (default: 'http://www.abbyy.com/FineReader_xml/FineReader10-schema-v1.xml')
    """
    def __init__(self, xml_file,  xml_namespace='http://www.abbyy.com/FineReader_xml/FineReader10-schema-v1.xml'):
        if self.__validate_xml_file(xml_file):
            self.namespace = xml_namespace
            
            # etree
            self.xml_file = xml_file
            self.__tree = None
            self.__root = None
            
            # Stores parsed data
            self.__parsed_texts = {}
        else:
            raise IOError('Invalid xml file')

    def __xpath(self, element, xpath, namespace_key='n'):
        """Helper function to execute etree.Element.xpath w/ namespace prefix
        
        :param element: <etree.Element> object
        :param xpath: xpath string
        :param namespace_key: <etree.Element> namespace map key (default: 'n')
        """
        namespace = {}
        namespace[namespace_key] = self.namespace

        return element.xpath(xpath, namespaces=namespace)

    def __parse_plaintiff_text(self):
        """Parse and return plaintiff text"""
        
        # Find the <line> elements where its child <formatting> element has text that starts with 'Plaintiff,'
        plaintiff_line_elem = self.__xpath(self.__root, './/n:line[n:formatting[starts-with(text(), "Plaintiff,")]]')
        plaintiff_right_bound = plaintiff_line_elem[0].get('l')
        
        # Find all <formatting> elements in between the 'COUNTY OF' and 'Plaintiff' elements
        # Also only find formatting texts that are positioned to the left of the 'Plaintiff,' <line>
        plaintiff_formatting_elems = self.__xpath(self.__root, 
                        ".//n:formatting[" \
                        "(preceding::n:formatting[contains(text(), 'COUNTY OF')])" \
                        " and " \
                        "(following::n:formatting[starts-with(text(), 'Plaintiff,')])" \
                        " and " \
                        "(ancestor::n:line[(@l < %s)])]" % (plaintiff_right_bound))

        # Iterate through all found <formatting> elements and strip out any text followed by 2 or more whitespaces
        # This is needed to exclude all text found on the right side of the document that should NOT be parsed
        return ' '.join(map(lambda elem: re.split('\s{2}', elem.text)[0], plaintiff_formatting_elems))

    def __parse_defendants_text(self):
        """Parse and return defendants text"""
        
        # Find the <line> elements where its child <formatting> element has text that starts with 'Defendants.'
        defendants_line_elem = self.__xpath(self.__root, './/n:line[n:formatting[starts-with(text(), "Defendants")]]')
        defendants_right_bound = defendants_line_elem[0].get('l')
        
        # Find all <formatting> elements in between the 'Plaintiff,' and 'Defendants.' elements
        # Also only find formatting texts that are positioned to the left of the 'Defendants.' <line>
        defendants_formatting_elems = self.__xpath(self.__root,
                        ".//n:formatting[" \
                        "(preceding::n:formatting[starts-with(text(), 'Plaintiff,')])" \
                        " and " \
                        "(following::n:formatting[starts-with(text(), 'Defendants.')])" \
                        " and " \
                        "(ancestor::n:line[(@l < %s)])]" % (defendants_right_bound))
        
        # Iterate through all found <formatting> elements and strip out any text followed by 2 or more whitespaces
        # This is needed to exclude all text found on the right side of the document that should NOT be parsed
        # We also exclude the first found <formatting> element as this will always be the 'vs.' or 'v.' text
        return ' '.join(map(lambda elem: re.split('\s{2}', elem.text)[0], defendants_formatting_elems[1:]))
    
    def extract(self):
        """Executes all private parse functions and return object map"""
        
        self.__tree = etree.parse(self.xml_file)
        self.__root = self.__tree.getroot()
        
        self.__parsed_texts['defendants'] = self.__parse_defendants_text()
        self.__parsed_texts['plaintiff'] = self.__parse_plaintiff_text()
        
        return self.get_parsed_texts()
    
    def get_parsed_texts(self):
        return self.__parsed_texts.copy()

    def __validate_xml_file(self, xml_file):
        """Returns True if valid correct xml file extension is used
        
        :param xml_file - <werkzeug.datastructures.FileStorage> object
        """
        if isinstance(xml_file, FileStorage):
            filename = xml_file.filename
            return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'xml'
        else:
            raise TypeError("Invalid FileStorage object")