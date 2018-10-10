import logging
from datetime import datetime
from collections import OrderedDict
from oaipmh import common
from oaipmh.error import IdDoesNotExistError, CannotDisseminateFormatError

from metashare.settings import LOG_HANDLER
from metashare.settings import COLLECTION_DISPLAY_NAME
from metashare.oaipmh.metadata_handlers import MetashareMap, OlacMap, CmdiMap
from metashare.storage.models import StorageObject, PUBLISHED

# Setup logging support.
LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(LOG_HANDLER)

from metashare.repository.metadata_pid import get_md_pid

class OaiPmhServer:
    """
    A server that responds to messages by returning OAI-PMH compliant XML.
    """
    def __init__(self, env):
        """
        Settings, required arguments are `name`, `url`, `adminEmails`.
        """
        self.env = env

    def identify(self):
        """
        OAI-PMH verb, identify.
        See http://www.openarchives.org/OAI/openarchivesprotocol.html#Identify
        """
        return common.Identify(
            repositoryName = self.env["repositoryName"],
            baseURL = self.env["baseURL"],
            protocolVersion = "2.0",
            adminEmails = self.env["adminEmails"],
            earliestDatestamp = datetime(2004, 1, 1),
            deletedRecord = 'transient',
            granularity = 'YYYY-MM-DDThh:mm:ssZ',
            compression = ['identity'])
    
    def getRecord(self, metadataPrefix, identifier):
        """
        OAI-PMH verb, GetRecord. See 
        http://www.openarchives.org/OAI/openarchivesprotocol.html#GetRecord
        """ 
        from metashare.repository.model_utils import get_lr_master_url   
        try:
            so = StorageObject.objects.get(identifier=identifier, publication_status=PUBLISHED)
        except:
            raise IdDoesNotExistError,'Resource [%s] does not exist' % identifier
        else:
            resource_sets = _get_setSpecs(so)
            header = (common.Header(identifier, so.modified, resource_sets, True) \
                      if so.deleted else common.Header(identifier, \
                                                       so.modified, \
                                                       resource_sets, \
                                                       False))
            if metadataPrefix == 'metashare':
                map_class = MetashareMap()
                map_ = map_class.getMap(so.metadata)
            elif metadataPrefix == 'olac':
                map_class = OlacMap()
                map_ = map_class.getMap(so.metadata)
            elif metadataPrefix == 'cmdi':
                map_class = CmdiMap()
                baseURL = self.env["baseURL"]
                request_url = '{0}?verb=GetRecord&identifier={1}&metadataPrefix=cmdi'.\
                            format(baseURL, identifier)
                resource = so.resourceinfotype_model_set.all()[0]
                pk = resource.pk
                absolute_url = get_lr_master_url(resource)
                map_ = _add_elements_to_cmdi_metadata( map_class.getMap(so.metadata), \
                                                     request_url, \
                                                     pk, \
                                                     absolute_url)
            else:
                raise CannotDisseminateFormatError, \
                    '%s metadata format is not supported' % metadataPrefix
            metadata = common.Metadata(map_)
            return header, metadata, None

    def listRecords(self, metadataPrefix=None, from_=None, until=None, set=None):
        """
        OAI-PMH verb, ListRecords.See 
        http://www.openarchives.org/OAI/openarchivesprotocol.html#ListRecords
        """
        def add_record(result, so, resource_sets):
            from metashare.repository.model_utils import get_lr_master_url
            id = so.identifier
            header = (common.Header(id, so.modified, resource_sets, True) \
                      if so.deleted else common.Header(id, \
                                                       so.modified, \
                                                       resource_sets, \
                                                       False))
            if datestampInRange(header, from_, until):
                if metadataPrefix == 'metashare':
                    map_class = MetashareMap()
                    map = map_class.getMap(so.metadata)
                elif metadataPrefix == 'olac':
                    map_class = OlacMap()
                    map = map_class.getMap(so.metadata)
                elif metadataPrefix == 'cmdi':
                    map_class = CmdiMap()
                    baseURL = self.env["baseURL"]
                    request_url = '{0}?verb=GetRecord&identifier={1}&metadataPrefix=cmdi'.\
                                format(baseURL,so.identifier)
                    resource = so.resourceinfotype_model_set.all()[0]
                    pk = resource.pk
                    absolute_url = get_lr_master_url(resource)
                    map = _add_elements_to_cmdi_metadata( map_class.getMap(so.metadata), \
                                                         request_url, \
                                                         pk, \
                                                         absolute_url)
                else:
                    raise CannotDisseminateFormatError, \
                        '%s metadata format is not supported' % metadataPrefix
                metadata = common.Metadata(map)
                result.append((header, metadata, None))

        storage_objects = get_storage_objects(from_, until)
        result = []
        if set:
            for so in storage_objects:
                resource_type = set.split(':')[0]
                resource_sets = _get_setSpecs(so) 
                if resource_type in resource_sets and set in resource_sets:
                    add_record(result, so, resource_sets)
        else:
            for so in storage_objects:
                resource_sets = _get_setSpecs(so)
                add_record(result, so, resource_sets) 
        return result
    
    def listIdentifiers(self, metadataPrefix=None, from_=None, until=None, set=None):
        """
        OAI-PMH verb, ListIdentifiers. See 
        http://www.openarchives.org/OAI/openarchivesprotocol.html#ListIdentifiers
        """
        def add_header(result, so, resource_sets):
            id = so.identifier
            header = (common.Header(id, so.modified, resource_sets, True) if so.deleted \
                        else common.Header(id, so.modified, resource_sets, False)) 
            if datestampInRange(header, from_, until):
                result.append(header)
                
        storage_objects = get_storage_objects(from_, until)                           
        result = []
        if set:
            for so in storage_objects:
                resource_type = set.split(':')[0]
                resource_sets = _get_setSpecs(so)
                if resource_type in resource_sets and set in resource_sets:
                    add_header(result, so, resource_sets)
        else:
            for so in storage_objects:
                resource_sets = _get_setSpecs(so)
                add_header(result, so, resource_sets)
        return result
    
    def listMetadataFormats(self, identifier=None):
        """
        OAI-PMH verb, ListMetadataFormats. See 
        http://www.openarchives.org/OAI/openarchivesprotocol.html#ListMetadataFormats
        """
        metadata_prefixies = ['metashare', 'olac', 'cmdi']
        schemata = ['http://metashare.ilsp.gr/META-XMLSchema/v3.0/META-SHARE-Resource.xsd', \
                    'http://www.language-archives.org/OLAC/1.1/olac.xsd', \
                    'http://catalog.clarin.eu/ds/ComponentRegistry/rest/registry/profiles/clarin.eu:cr1:p_1271859438204/xsd']
        namespaces = ['http://www.ilsp.gr/META-XMLSchema', \
                      'http://www.language-archives.org/OLAC/1.1/', \
                      'http://www.clarin.eu/cmd/']
        formats = zip(metadata_prefixies, schemata, namespaces)
        return formats
    
    def listSets(self):
        """
        OAI-PMH verb, ListSets.
        See http://www.openarchives.org/OAI/openarchivesprotocol.html#ListSets
        """
        sets = zip(setSpec, setName, setName)
        return sets
    
def get_storage_objects(from_, until):
    if from_:
        storage_objects = (StorageObject.objects.filter(publication_status=PUBLISHED, modified__gte=from_).\
                           filter(modified__lte=until) \
                           if until else StorageObject.objects.\
                            filter(publication_status=PUBLISHED, modified__gte=from_))
    elif until:
        storage_objects = StorageObject.objects.\
            filter(publication_status=PUBLISHED, modified__lte=until)
    else:
        storage_objects = StorageObject.objects.\
            filter(publication_status=PUBLISHED)
    return storage_objects


def datestampInRange(header, from_, until):
    if from_ is not None and header.datestamp() < from_:
        return False
    if until is not None and header.datestamp() > until:
        return False
    return True

def _get_setSpecs(storage_object):
    """
    the sets to which the resource belongs
    """
    import itertools
    from metashare.repository.models import corpusInfoType_model, \
        lexicalConceptualResourceInfoType_model, \
        languageDescriptionInfoType_model, toolServiceInfoType_model
    from metashare.repository.model_utils import get_resource_media_types
    
    set_ = []
    resource = storage_object.resourceinfotype_model_set.all()[0]
    resourceComponentType = resource.resourceComponentType.as_subclass()
    resource_type = resourceComponentType.resourceType
    if isinstance(resourceComponentType, corpusInfoType_model):
        # sets are the media types, e.g text 
        types = get_resource_media_types(resource) 
    elif isinstance(resourceComponentType, lexicalConceptualResourceInfoType_model):
        # sets are the resource types, e.g ontology 
        types = [resourceComponentType.lexicalConceptualResourceType] 
    elif isinstance(resourceComponentType, languageDescriptionInfoType_model):
        # sets are the resource types, e.g grammar 
        types = [resourceComponentType.languageDescriptionType] 
    elif isinstance(resourceComponentType, toolServiceInfoType_model): 
        # sets are the resource types, e.g platform
        types = [resourceComponentType.toolServiceType] 
    
    # remove duplicates and preserver order
    seen = set()
    seen_add = seen.add
    types = [x for x in types if x not in seen and not seen_add(x)]

    # types are less than 10, so map each type to an int
    map_type_to_int = OrderedDict()       
    for counter, type_ in enumerate(types):
        map_type_to_int[str(counter)] = type_
    
    # convert the integer strings to a string sequence
    # and make all the possible combinations, between its chars
    str_types = ''.join(map_type_to_int.keys())
    for i in range(len(types)):
        for int_comb_type in itertools.combinations(str_types, i+1):
            comb_type = resource_type
            for int_ in int_comb_type:
                comb_type += ':{}'.format(map_type_to_int[int_])
            set_.append(comb_type)
    set_.insert(0, resource_type)

    ## #the source repository of the resource
    ## set_.insert(0,storage_object.source_url)
    return set_
    
def _add_elements_to_cmdi_metadata( map_, request_url, pk, absolute_url ):
    from lxml import etree

    msId = absolute_url.split('/')[-2]

    cmdi_xml = etree.tostring(map_['CMD'])
    cmdi_elem = etree.fromstring(cmdi_xml)
    resourcePid = None

    for child in cmdi_elem:
        if child.tag.strip() == '{http://www.clarin.eu/cmd/}Header':
            elem = etree.SubElement(child, 'MdSelfLink')
            elem.text = absolute_url
            # MdCollectionDisplayName, set in local_settings.py
            elema = etree.SubElement(child, 'MdCollectionDisplayName')
            elema.text = COLLECTION_DISPLAY_NAME
        if child.tag.strip() == '{http://www.clarin.eu/cmd/}Resources':
            resourceProxyList_elem = child[0]
            resourceProxy_elem = etree.SubElement(resourceProxyList_elem, \
                                                  'ResourceProxy')
            resourceProxy_elem.attrib['id'] = 'resource-{}'.format(pk)
            resourceType_elem = etree.SubElement(resourceProxy_elem, \
                                                 'ResourceType')
            resourceType_elem.text = 'LandingPage'
            resourceRef_elem = etree.SubElement(resourceProxy_elem, \
                                                'ResourceRef')
            resourceRef_elem.text = absolute_url
        # For metaShareId
        if child.tag.strip() == '{http://www.clarin.eu/cmd/}Components':
            for cchild in child[0][0]:
                if cchild.tag == '{http://www.clarin.eu/cmd/}metaShareId':
                    cchild.text = msId
                # get Resource PID
                if cchild.tag == '{http://www.clarin.eu/cmd/}identifier':
                    resourcePid = cchild.text.strip()

    map_['CMD'] = cmdi_elem

    cmdi_xml = etree.tostring(map_['CMD'])
    cmdi_elem = etree.fromstring(cmdi_xml)

    if resourcePid:
    # insert Metadata PID according to Resource PID
        for child in cmdi_elem:
            if child.tag.strip() == '{http://www.clarin.eu/cmd/}Header':
                for cchild in child:
                    if cchild.tag.strip() == '{http://www.clarin.eu/cmd/}MdSelfLink':
                    # child.text = get_md_pid(resourcePid)
                        cchild.text = get_md_pid(resourcePid)

    
    map_['CMD'] = cmdi_elem
    return map_
        
setSpec = ['corpus', 'languageDescription', 'lexicalConceptualResource', 
           'toolService', 'corpus:text', 'corpus:audio', 'corpus:video', 
           'corpus:textngram', 'corpus:image', 'corpus:textnumerical', 
           'corpus:text:audio', 'corpus:text:video', 'corpus:text:textngram', 
           'corpus:text:image', 'corpus:text:textnumerical', 
           'corpus:audio:video', 
           'corpus:audio:textngram', 'corpus:audio:image', 
           'corpus:audio:textnumerical', 
           'corpus:video:textngram', 'corpus:video:image', 
           'corpus:video:textnumerical', 
           'corpus:textngram:image', 'corpus:textngram:textnumerical', 
           'corpus:image:textnumerical', 'corpus:text:audio:video', 
           'corpus:text:audio:textngram', 'corpus:text:audio:image', 
           'corpus:text:audio:textnumerical', 'corpus:text:video:textngram', 
           'corpus:text:video:image', 'corpus:text:video:textnumerical', 
           'corpus:text:textngram:image', 'corpus:text:textngram:textnumerical', 
           'corpus:text:image:textnumerical', 'corpus:audio:video:textngram', 
           'corpus:audio:video:image', 'corpus:audio:video:textnumerical', 
           'corpus:audio:textngram:image', 
           'corpus:audio:textngram:textnumerical', 
           'corpus:audio:image:textnumerical', 'corpus:video:textngram:image', 
           'corpus:video:textngram:textnumerical', 
           'corpus:video:image:textnumerical', 
           'corpus:textngram:image:textnumerical', 
           'corpus:text:audio:video:textngram', 
           'corpus:text:audio:video:image', 
           'corpus:text:audio:video:textnumerical', 
           'corpus:text:audio:textngram:image', 
           'corpus:text:audio:textngram:textnumerical', 
           'corpus:text:audio:image:textnumerical', 
           'corpus:text:video:textngram:image', 
           'corpus:text:video:textngram:textnumerical', 
           'corpus:text:video:image:textnumerical', 
           'corpus:text:textngram:image:textnumerical', 
           'corpus:audio:video:textngram:image', 
           'corpus:audio:video:textngram:textnumerical', 
           'corpus:audio:video:image:textnumerical', 
           'corpus:audio:textngram:image:textnumerical', 
           'corpus:video:textngram:image:textnumerical', 
           'corpus:text:audio:video:textngram:image', 
           'corpus:text:audio:video:textngram:textnumerical', 
           'corpus:text:audio:video:image:textnumerical', 
           'corpus:text:audio:textngram:image:textnumerical', 
           'corpus:text:video:textngram:image:textnumerical', 
           'corpus:audio:video:textngram:image:textnumerical', 
           'corpus:text:audio:video:textngram:image:textnumerical', 
           'languageDescription:grammar', 'languageDescription:other', 
           'lexicalConceptualResource:wordList', 
           'lexicalConceptualResource:computationalLexicon', 
           'lexicalConceptualResource:ontology', 
           'lexicalConceptualResource:wordnet', 
           'lexicalConceptualResource:thesaurus',
           'lexicalConceptualResource:framenet', 
           'lexicalConceptualResource:terminologicalResource',
           'lexicalConceptualResource:machineReadableDictionary', 
           'lexicalConceptualResource:lexicon', 
           'lexicalConceptualResource:other', 
           'toolService:tool', 'toolService:service', 
           'toolService:platform', 'toolService:suiteOfTools', 
           'toolService:infrastructure', 'toolService:architecture',
           'toolService:nlpDevelopmentEnvironment', 'toolService:other'
                  ]
setName = ['Corpus', 'Language Description', 'Lexical Conceptual Resource', 
           'Tools/Service',
           'Corpus of text media type', 'Corpus of audio media type', 
           'Corpus of video media type', 'Corpus of textNGram media type', 
           'Corpus of image media type', 'Corpus of textNumerical media type',
           'Corpus of media type: text, audio', 
           'Corpus of media type: text, video', 
           'Corpus of media type: text, textNgram', 
           'Corpus of media type: text, image', 
           'Corpus of media type: text, textNumerical',
           'Corpus of media type: audio, video', 
           'Corpus of media type: audio, textNgram', 
           'Corpus of media type: audio, image', 
           'Corpus of media type: audio, textNumerical',
           'Corpus of media type: video, textNgram', 
           'Corpus of media type: video, image', 
           'Corpus of media type: video, textNumerical', 
           'Corpus of media type: textNgram, image', 
           'Corpus of media type: textNgram, textNumerical', 
           'Corpus of media type: image, textNumerical',
           'Corpus of media type: text, audio, video', 
           'Corpus of media type: text, audio, textNgram', 
           'Corpus of media type: text, audio, image', 
           'Corpus of media type: text, audio, textNumerical',
           'Corpus of media type: text, video, textNgram', 
           'Corpus of media type: text, video, image', 
           'Corpus of media type: text, video, textNumerical', 
           'Corpus of media type: text, textNgram, image', 
           'Corpus of media type: text, textNgram, textNumerical', 
           'Corpus of media type: text, image, textNumerical',
           'Corpus of media type: audio, video, textNgram ', 
           'Corpus of media type: audio, video, image',  
           'Corpus of media type: audio, video, textNumerical', 
           'Corpus of media type: audio, textNgram,  image', 
           'Corpus of media type: audio, textNgram, textNumerical', 
           'Corpus of media type: audio, image, textNumerical',
           'Corpus of media type: video, textNgram, image', 
           'Corpus of media type: video, textNgram, textNumerical',
           'Corpus of media type: video, image, textNumerical', 
           'Corpus of media type: textNgram, image, textNumerical',
           'Corpus of media type: text, audio, video, textNgram', 
           'Corpus of media type: text, audio, video, image',
           'Corpus of media type: text, audio, video, textNumerical', 
           'Corpus of media type: text, audio, textNgram, image',
           'Corpus of media type: text, audio, textNgram, textNumerical', 
           'Corpus of media type: text, audio, image, textNumerical',
           'Corpus of media type: text, video, textNgram, image',
           'Corpus of media type: text, video, textNgram, textNumerical', 
           'Corpus of media type: text, video, image, textNumerical',
           'Corpus of media type: text, textNgram, image, textNumerical', 
           'Corpus of media type: audio, video, textNgram, image',
           'Corpus of media type: audio, video, textNgram, textNumerical', 
           'Corpus of media type: audio, video, image, textNumerical',
           'Corpus of media type: audio, textNgram, image, textNumerical', 
           'Corpus of media type: video, textNgram, image, textNumerical',            
           'Corpus of media type: text, audio, video, textNgram, image', 
           'Corpus of media type: text, audio, video, textNgram, textNumerical',
           'Corpus of media type: text, audio, video, image, textNumerical',
           'Corpus of media type: text, audio, textNgram, image, textNumerical', 
           'Corpus of media type: text, video, textNgram, image, textNumerical',
           'Corpus of media type: audio, video, textNgram, image, textNumerical',  
           'Corpus of media type: text, audio, video, textNgram, image, textNumerical',
           'Grammar', 'Other than grammar language description type', 
           'Word list', 'computational lexicon', 'Ontology', 'Wordnet', 
           'Thesaurus', 'Framenet', 'Terminological resource', 
           'Machine readable dictionary', 'Lexicon', 
           'Other lexical conceptual resource', 'Tool', 'Service', 'Platform',
           'Suite of tools', 'Infrastructure', 'Architecture', 
           'Nlp development enviroment',
           'Other service or tool']
