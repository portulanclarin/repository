# coding=utf-8
import logging

from oaipmh import common
from lxml import etree
from metashare.settings import LOG_HANDLER, ROOT_PATH 

# Setup logging support.
LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(LOG_HANDLER)

def _parse_from_unicode(unicode_str):
    """
    Parses the string and returns an etree tree
    """
    utf8_parser = etree.XMLParser(encoding='utf-8', \
                                  remove_blank_text=True, \
                                  ns_clean=True)
    encoded_str = unicode_str.encode('utf-8')
    return etree.fromstring(encoded_str, parser=utf8_parser)

def _transform_xml(xml, xslt_path):
    """
    Converts the xml document from one metadata schema to another
    """
    xslt_file = open('{0}/../misc/tools/{1}'.format(ROOT_PATH, xslt_path))
    xslt_root = etree.parse(xslt_file)
    transform = etree.XSLT(xslt_root)
    return transform(xml)

class Reader:
    """
    Implementation of a reader. A reader takes a chunk of (parsed) XML and
    returns a metadata object.
    """
    def __init__(self):
        pass

    def __call__(self, metashare_elem ):
        xml = etree.tostring(metashare_elem[0], pretty_print=True )
        return common.Metadata({ "raw_xml": xml })
      
class MetashareWriter:
    """
    Implementation of a writer. A writer takes a takes a metadata object and
    produces a chunk of XML in the right format for this metadata.
    """
    def __init__(self):
        pass
    
    def __call__(self, element, metadata):
        map_ = metadata.getMap()
        #map contains only the root Element of the ElementTree
        root_elem = map_['resourceInfo']
        element.append(root_elem.getroot())
        
class OlacWriter:
    """
    Implementation of a writer. A writer takes a takes a metadata object and
    produces a chunk of XML in the right format for this metadata.
    """
    def __init__(self):
        pass
    
    def __call__(self, element, metadata):
        map_ = metadata.getMap()
        #map contains only the ElementTree
        root_elem = map_['metadataInfo']
        element.append(root_elem.getroot())
        
class CmdiWriter:
    """
    Implementation of a writer. A writer takes a takes a metadata object and
    produces a chunk of XML in the right format for this metadata.
    """
    def __init__(self):
        pass
    
    def __call__(self, element, metadata):
        map_ = metadata.getMap()
        #map contains only the root element
        root_elem = map_['CMD']
        element.append(root_elem)
                           
class MetashareMap:
    """
    """
    def __init__( self ):
        pass
    
    def getMap(self, raw_xml_record):
        map = {}       
        root = _parse_from_unicode(raw_xml_record)
        tree = root.getroottree()
        map['resourceInfo'] = tree
        return map


class OlacMap:
    """
    """
    def __init__( self ):
        pass
    
    def getMap(self, raw_xml_record):
        map_ = {}
        root = _parse_from_unicode(raw_xml_record)
        tree = root.getroottree()
        xslt_path = 'OLACConverters/metashareToOlac.xsl'
        olac_root = _transform_xml(tree, xslt_path)
        map_['metadataInfo'] = olac_root
        return map_
        
class CmdiMap:
    """
    """
    def __init__( self ):
        pass
    
    def getMap(self, raw_xml_record):
        map_ = {}
        root = _parse_from_unicode(raw_xml_record)
        tree = root.getroottree()
        xslt_path = 'CMDIConverters/metashareToCmdi.xsl'
        cmdi_root = _transform_xml(tree, xslt_path)
        map_['CMD'] = cmdi_root
        return map_
        


        
