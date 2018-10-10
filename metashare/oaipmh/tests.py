import logging
import os
from lxml import etree
from datetime import datetime, timedelta
from StringIO import StringIO
from django.test import TestCase

from metashare import settings, test_utils
from metashare.oaipmh import oaipmh_server
from metashare.storage.models import PUBLISHED, INGESTED

# Setup logging support.
LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(settings.LOG_HANDLER)

# load up schema
oaischema = etree.XMLSchema(etree.parse(os.path.join('/opt/META-SHARE_versions/META-SHARE_OAI-PMH/lib/python2.7/site-packages/oaipmh/tests/','OAI-PMH.xsd')))

def import_test_resource(filename, publication_status, deleted=False):
    _fixture = '{0}/repository/fixtures/{1}'.format(settings.ROOT_PATH, filename)
    resource = test_utils.import_xml(_fixture)
    resource.storage_object.publication_status = publication_status
    resource.storage_object.deleted = deleted
    resource.storage_object.save()
    resource.storage_object.update_storage()
    return resource

class ServerTestCase(TestCase):
    
    @classmethod
    def setUpClass(cls):
        LOGGER.info("running '{}' tests...".format(cls.__name__))
        test_utils.set_index_active(False)

    @classmethod
    def tearDownClass(cls):
        test_utils.set_index_active(True)
        LOGGER.info("finished '{}' tests".format(cls.__name__))
        
    def setUp(self):
        test_utils.setup_test_storage()
        
        # text corpus
        self.testres1 = import_test_resource('testfixture.xml', PUBLISHED)
        # text corpus
        self.ing_testres = import_test_resource('completiontestfixture.xml', INGESTED)
        # lexical conceptual resource
        self.testres3 = import_test_resource('roundtrip.xml', PUBLISHED)
        # text corpus
        self.del_testres = import_test_resource('ILSP10.xml', PUBLISHED, True)
        # text, video, audio, textNumerical corpus
        self.testres5 = import_test_resource('ILSP11.xml', PUBLISHED)
        # tool/service
        self.testres6 = import_test_resource('local_download.xml', PUBLISHED)
        
    def tearDown(self):
        """
        Removes the storage object instance from the database after testing.
        """
        test_utils.clean_resources_db()
        test_utils.clean_storage()
        
    ## def test_getRecord(self):
        ## # get a published record
        ## resource_id = self.testres1.storage_object.identifier
        ## xml = oaipmh_server.handleRequest({'verb': 'GetRecord',
                                           ## 'identifier':resource_id,
                                           ## 'metadataPrefix':'metashare'})
        ## tree = etree.parse(StringIO(xml))
        ## self.assertTrue(oaischema.validate(tree))
        ## self.assertEquals(len(tree.xpath('//t:header', 
                                        ## namespaces={'t':'http://www.openarchives.org/OAI/2.0/'})),1)
        ## self.assertEquals(len(tree.xpath('//t:metadata', 
                                        ## namespaces={'t':'http://www.openarchives.org/OAI/2.0/'})),1) 
        
        ## # get a published, deleted record
        ## resource_id = self.del_testres.storage_object.identifier
        ## xml = oaipmh_server.handleRequest({'verb': 'GetRecord',
                                           ## 'identifier':resource_id,
                                           ## 'metadataPrefix':'metashare'})
        ## tree = etree.parse(StringIO(xml))
        ## self.assertTrue(oaischema.validate(tree))
        ## self.assertEquals(len(tree.xpath('//t:header', 
                                        ## namespaces={'t':'http://www.openarchives.org/OAI/2.0/'})),1)
        ## # the deleted record has no metadata element
        ## self.assertEquals(len(tree.xpath('//t:metadata', 
                                    ## namespaces={'t':'http://www.openarchives.org/OAI/2.0/'})),0)
                                    
        
    #DONE!    
    ## def test_identify(self):
        ## """
        ## Verifies that the response in the request identify returns 
        ## valid xml tree 
        ## """
        ## xml = oaipmh_server.handleRequest({'verb': 'Identify'})
        ## tree = etree.parse(StringIO(xml))
        ## self.assertTrue(oaischema.validate(tree))

    #DONE!
    ## def test_listIdentifiers(self):
        ## valid_formats = ["metashare", "cmdi", "olac"]
        ## for format in valid_formats:
            ## xml = oaipmh_server.handleRequest({'verb': 'ListIdentifiers',
                ## 'set':'corpus:text',
                ## 'metadataPrefix':format})
            ## tree = etree.parse(StringIO(xml))
            ## self.assertTrue(oaischema.validate(tree))
            ## self.assertEquals(len(tree.xpath('//t:header', 
                                             ## namespaces={'t':'http://www.openarchives.org/OAI/2.0/'})),3)
                                             
    def test_listIdentifiersFromUntil(self):
        valid_formats = ["metashare", "cmdi", "olac"]
        tomorrow = datetime.now()+timedelta(days=1)
        u = tomorrow.strftime('%Y-%m-%d %H:%M:%S')
        print 'tomorrow ', u
        for format in valid_formats:
            xml = oaipmh_server.handleRequest({'verb': 'ListIdentifiers',
                'metadataPrefix':format,
                'from_' : '2014-04-05',
                'until': tomorrow.strftime('%Y-%m-%dT%H:%M:%SZ'),
                })
            tree = etree.parse(StringIO(xml))
            self.assertTrue(oaischema.validate(tree))
            self.assertEquals(len(tree.xpath('//t:header', 
                                             namespaces={'t':'http://www.openarchives.org/OAI/2.0/'})),5)
    
    def test_listIdentifiersFromUntil_nothing(self):
        valid_formats = ["metashare", "cmdi", "olac"]
        yesterday = datetime.now()+timedelta(days=-1)
        for format in valid_formats:
            xml = oaipmh_server.handleRequest({'verb': 'ListIdentifiers',
                'metadataPrefix':format,
                'from_' : '2011-04-05',
                'until': yesterday.strftime('%Y-%m-%dT%H:%M:%SZ'),
                })
            tree = etree.parse(StringIO(xml))
            print 'xml ', xml
            self.assertTrue(oaischema.validate(tree))
            self.assertEquals(len(tree.xpath("//t:error[@code='noRecordsMatch']", 
                                             namespaces={'t':'http://www.openarchives.org/OAI/2.0/'})),1)
        
    ## def test_listMetadataFormats(self):
        ## """
        ## Verifies that the response in the request listMetadataFormats returns 
        ## valid xml tree 
        ## """
        ## xml = oaipmh_server.handleRequest({'verb': 'ListMetadataFormats'})
        ## tree = etree.parse(StringIO(xml))
        ## self.assertTrue(oaischema.validate(tree))

    ## def test_listRecords(self):
        ## valid_formats = ["metashare", "cmdi", "olac"]
        ## for format in valid_formats:
            ## xml = oaipmh_server.handleRequest({'verb': 'ListRecords',
                ## 'from_':datetime(2014, 4, 23),
                ## ## 'until':datetime.now(),
                ## 'set':'corpus:text',
                ## 'metadataPrefix':format})
            ## tree = etree.parse(StringIO(xml))
            ## self.assertTrue(oaischema.validate(tree))
            ## self.assertEquals(len(tree.xpath('//t:header', 
                                             ## namespaces={'t':'http://www.openarchives.org/OAI/2.0/'})),3)
            ## # the deleted record has no metadata element
            ## self.assertEquals(len(tree.xpath('//t:metadata', 
                                    ## namespaces={'t':'http://www.openarchives.org/OAI/2.0/'})),2)

    #DONE!
    ## def test_listSets(self):
        ## """
        ## Verifies that the response in the request listSets returns 
        ## valid xml tree 
        ## """
        ## xml = oaipmh_server.handleRequest({'verb': 'ListSets'})
        ## tree = etree.parse(StringIO(xml))
        ## self.assertTrue(oaischema.validate(tree))
        
## class ErrorTestCase(unittest.TestCase):
    ## @classmethod
    ## def setUpClass(cls):
        ## LOGGER.info("running '{}' tests...".format(cls.__name__))
        ## test_utils.set_index_active(False)

    ## @classmethod
    ## def tearDownClass(cls):
        ## test_utils.set_index_active(True)
        ## LOGGER.info("finished '{}' tests".format(cls.__name__))
        
    ## def setUp(self):
        ## test_utils.setup_test_storage()
        
        ## # text corpus
        ## self.testres1 = import_test_resource('testfixture.xml', PUBLISHED)
        ## # text corpus
        ## self.ing_testres = import_test_resource('completiontestfixture.xml', INGESTED)
        ## # lexical conceptual resource
        ## self.testres3 = import_test_resource('roundtrip.xml', PUBLISHED)
        ## # text corpus
        ## self.del_testres = import_test_resource('ILSP10.xml', PUBLISHED, True)
        ## # text, video, audio, textNumerical corpus
        ## self.testres5 = import_test_resource('ILSP11.xml', PUBLISHED)
        ## # tool/service
        ## self.testres6 = import_test_resource('local_download.xml', PUBLISHED)
        
    ## def tearDown(self):
        ## """
        ## Removes the storage object instance from the database after testing.
        ## """
        ## test_utils.clean_resources_db()
        ## test_utils.clean_storage()
        
    ## def setUp(self):
        ## self._fakeserver = fakeserver.FakeServer()
        ## metadata_registry = metadata.MetadataRegistry()
        ## metadata_registry.registerWriter('oai_dc', server.oai_dc_writer)
        ## metadata_registry.registerReader('oai_dc', metadata.oai_dc_reader)
        ## self._server = server.Server(self._fakeserver, metadata_registry,
                                     ## resumption_batch_size=7)

    ## def test_badArgument(self):
        ## xml = xml = oaipmh_server.handleRequest({'verb': 'Identify',
                                          ## 'foo' : 'Bar'})
        ## tree = etree.parse(StringIO(xml))
        ## self.assertTrue(oaischema.validate(tree))
        ## self.assertEquals(len(tree.xpath("//t:error[@code='badArgument']", 
                                             ## namespaces={'t':'http://www.openarchives.org/OAI/2.0/'})),1)
        ## # need more tests for different variations (required, etc)

    ## def test_noArgument(self):
        ## xml = oaipmh_server.handleRequest({})
        ## self.assertTrue(oaischema.validate(tree))
        ## self.assertEquals(len(tree.xpath("//t:error[@code='badVerb']", 
                                             ## namespaces={'t':'http://www.openarchives.org/OAI/2.0/'})),1)
        ## self.assertErrors([('badVerb', 'Required verb argument not found.')],
                          ## xml)
        
    ## def test_badVerb(self):
        ## xml = oaipmh_server.handleRequest({'verb': 'Frotz'})
        ## self.assertEquals(len(tree.xpath("//t:error[@code='badVerb']", 
                                             ## namespaces={'t':'http://www.openarchives.org/OAI/2.0/'})),1)
        ## self.assertErrors([('badVerb', 'Illegal verb: Frotz')], xml)

    ## def test_badResumptionToken(self):
        ## xml = self._server.handleRequest({'verb': 'ListRecords',
                                          ## 'resumptionToken': 'foobar'})
        ## self.assertErrors(
            ## [('badResumptionToken',
             ## 'Unable to decode resumption token: foobar')], xml)

    ## def test_cannotDisseminateFormat(self):
        ## xml = self._server.handleRequest({'verb': 'ListRecords',
                                          ## 'metadataPrefix': 'nonexistent'})
        ## self.assertErrors(
            ## [('cannotDisseminateFormat',
              ## 'Unknown metadata format: nonexistent')],
            ## xml)

    ## def test_idDoesNotExist(self):
        ## xml = self._server.handleRequest({'verb': 'GetRecord',
                                          ## 'metadataPrefix': 'oai_dc',
                                          ## 'identifier': '500'})
        ## self.assertErrors(
            ## [('idDoesNotExist',
              ## 'Id does not exist: 500')],
            ## xml)

    ## def test_badDateArgument(self):
        ## xml = self._server.handleRequest({'verb': 'ListRecords',
                                          ## 'metadataPrefix': 'oai_dc',
                                          ## 'from': 'junk'})
        ## self.assertErrors(
            ## [('badArgument',
              ## "The value 'junk' of the argument 'from' is not valid.")],
            ## xml)
        ## xml = self._server.handleRequest({'verb': 'ListRecords',
                                          ## 'metadataPrefix': 'oai_dc',
                                          ## 'until': 'junk'})
        ## self.assertErrors(
            ## [('badArgument',
              ## "The value 'junk' of the argument 'until' is not valid.")],
            ## xml)


    ## def testDifferentGranularities(self):
        ## xml = self._server.handleRequest({'verb': 'ListRecords',
                                          ## 'metadataPrefix': 'oai_dc',
                                          ## 'from': '2006-01-01',
                                          ## 'until': '2008-01-01T00:00:00Z'})
        ## self.assertErrors(
            ## [('badArgument',
              ## "The request has different granularities for the from"
              ## " and until parameters")],
            ## xml)
        
    
    ## def assertErrors(self, errors, xml):
        ## self.assertEquals(errors, self.findErrors(xml))
        
    ## def findErrors(self, xml):
        ## # parse
        ## tree = etree.parse(StringIO(xml))
        ## # validate xml
        ## self.assert_(oaischema.validate(tree))
        ## result = []
        ## for e in tree.xpath(
            ## '//oai:error', namespaces={'oai': NS_OAIPMH}):
            ## result.append((e.get('code'), e.text))
        ## result.sort()
        ## return result
        