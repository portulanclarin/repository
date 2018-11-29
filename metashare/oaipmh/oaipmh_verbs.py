# coding=utf-8
import os
import logging
import cgi
from collections import OrderedDict
from lxml import etree
from hashlib import md5
import json

from oaipmh.client import Client
from oaipmh.metadata import MetadataRegistry
from oaipmh.datestamp import datestamp_to_datetime

from metashare.settings import LOG_HANDLER, DJANGO_URL, STORAGE_PATH, ROOT_PATH
from metashare.oaipmh.models import OAIPMHRepository
from metashare.oaipmh.metadata_handlers import Reader
from metashare.oaipmh._utils import *
from metashare.storage.models import INGESTED, MASTER, add_or_update_resource
from metashare.xml_utils import import_from_string
from metashare.stats.model_utils import saveLRStats, DELETE_STAT

# Setup logging support.
LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(LOG_HANDLER)

def _client(base_URL, registry=None):
    """
    instantiate client
    """
    client = Client(base_URL, registry)
    return client

def _registerReader(metadata_format):
    """
    """
    #TODO, check namespaces
    if metadata_format in ("metashare", "cmdi", "olac"):
        metadata_registry = MetadataRegistry()
        metadata_registry.registerReader(metadata_format, Reader())
        return metadata_registry
    else:
        raise NotImplementedError("The %s metadata format is " \
                                  "currently not supported." % metadata_format)


def ListRecords(kwargs):
    """
    List all records.
    @required: url, metadata_format
    @return: dict of displayable items
    """
    base_URL, metadata_format, from_, until, set_ = get_values(kwargs,
                                                      ("base_URL", \
                                                       "metadata_format",
                                                       "from_", \
                                                       "until", \
                                                       "set_"))
    from_ = (None if not from_ else datestamp_to_datetime(from_))
    until = (None if not until else datestamp_to_datetime(until))
    client = _client(base_URL, _registerReader(metadata_format))
    dict_ = {}
    for header, metadata, about in client.listRecords(metadataPrefix=metadata_format, \
                                                      from_=from_, \
                                                      until=until, \
                                                      set=set_):
        if not header.isDeleted():
            data_str = prehtmlify(metadata.getMap(),
                                  add_pre=False)
            data_str = data_str.replace(u"\\n", u"\n").splitlines()
            data_str = [cgi.escape(x) for x in data_str \
                        if not 0 == len(x.strip())]
            dict_[header.identifier()] = u"<br>".join(data_str)
        else:
            dict_[header.identifier()] = u"<br>is Deleted."
    return dict_

def ListSets(kwargs):
    """
    Renders the list of the client's repository sets.
    """
    base_URL = get_values(kwargs, ("base_URL",))
    client = _client(base_URL)
    dict_ = {}
    for spec, name, description in client.listSets():
        dict_[spec] = prehtmlify((
            u"name: %s" % name,
            u"spec: %s" % spec,
            u"description: %s" % description,
        ))
    return dict_

def ListMetadataFormats(kwargs):
    """
    Renders the list of the client's repository metadata formats.
    """
    base_URL = get_values(kwargs, ("base_URL",))
    client = _client(base_URL)
    dict_ = {}
    for prefix, schema, ns in client.listMetadataFormats():
        dict_[prefix] = prehtmlify((
            u"prefix: %s" % prefix,
            u"schema: %s" % schema,
            u"ns: %s" % ns,
        ))
    return dict_

def ListIdentifiers(kwargs):
    """
    Renders the list of the client's repository record identifiers.
    """
    base_URL, metadata_format, from_, until, set_ = \
        get_values(kwargs, ("base_URL", \
                            "metadata_format", \
                            "from_", \
                            "until", \
                            "set_"))
    client = _client(base_URL)
    from_ = (None if not from_ else datestamp_to_datetime(from_))
    until = (None if not until else datestamp_to_datetime(until))
    dict_ = {}
    for id_ in client.listIdentifiers(metadataPrefix=metadata_format, \
                                      from_=from_, \
                                      until=until, \
                                      set=set_):
        sets = id_.setSpec()
        #if the repository does not support sets
        sets = ('' if len(sets)==0 else sets)
        dict_[id_.identifier()] = sets
    return dict_

def Identify(kwargs):
    """
    Renders the client's repository identification.
    """
    base_URL = get_values(kwargs, ("base_URL",))
    client = _client(base_URL)
    dict_ = {}
    id_ = client.identify()
    dict_["repository Name"] = id_.repositoryName()
    dict_["base URL"] = id_.baseURL()
    dict_["Protocol version"] = id_.protocolVersion()
    dict_["Admin emails"] = id_.adminEmails()
    return dict_

def harvest(base_URL='http://www.language-archives.org/cgi-bin/olaca3.pl',
            metadata_format='olac', remote_id=None, from_=None, until=None,
            set_=None, return_=False ):
    """
    Harvests record(s) from the client's repository.
    """
    OK_MSG = u"OK"
    from_ = (None if not from_ else datestamp_to_datetime(from_))
    until = (None if not until else datestamp_to_datetime(until))
    ret_d = OrderedDict()
    client = _client(base_URL, _registerReader(metadata_format))
    # get or create client's repository
    repository_name = client.identify().repositoryName()
    repository, _created = OAIPMHRepository.objects.get_or_create(repository_name=repository_name)
    LOGGER.info(u'OAI-PMH: Harvesting from {} repository'.format(repository_name))
    # harvest one or a list of records
    if remote_id:
        header, metadata, about = client.getRecord(metadataPrefix=metadata_format, \
                                                   identifier=remote_id)
        try:
            if header.isDeleted():
                deleted = _delete_resource(repository, remote_id)
                ret_d[remote_id] = html_mark_warning(u"This record is deleted.")
                if deleted:
                    LOGGER.info(u"OAI-PMH: Resource [%s] successfully deleted.", \
                                header.identifier())
            # add or update resource
            raw_xml_record = metadata.getField("raw_xml")
            if not repository.contains(remote_id):
                source_url = (header.setSpec()[0] \
                              if (metadata_format in 'metashare' \
                                  and 'META-SHARE' in repository_name) or \
                                  'META-SHARE' in repository_name else None)
                resource = _add_resource(repository, remote_id, \
                                         metadata_format, raw_xml_record, \
                                         source_url)
                LOGGER.info(u"OAI-PMH: Resource [%s] successfully added.", \
                            resource.pk)
            else:
                resource, updated = _update_resource(repository, remote_id, \
                                                     metadata_format, \
                                                     raw_xml_record)
                if updated:
                    LOGGER.info(u"OAI-PMH: Resource [%s] successfully updated.", \
                                resource.pk)
            resource_name = resource.identificationInfo.get_default_resourceName()
            ret_d[remote_id] = OK_MSG, \
                            repr(resource_name), \
                            resource.storage_object.identifier
        except Exception, exc:
            LOGGER.error(exc, exc_info=True)
            ret_d[remote_id] = html_mark_error(repr(exc))
    else:
        list_records =  (client.listRecords(metadataPrefix=metadata_format, \
                                            from_=from_, \
                                            until=until, \
                                            set=set_)
                            if set_ else client.listRecords(metadataPrefix=metadata_format, \
                                                     from_=from_, \
                                                     until=until))

        count_deleted_resources = 0
        resources_to_add = {}
        resources_to_update = {}
        # iterate the records and i) delete the records, which have the flag isDeleted=True,
        # ii) add the records that are not in the repository and iii) update the records that
        # have updated metadata
        for header, metadata, about in list_records:
            remote_id = header.identifier()
            if header.isDeleted():
                try:
                    deleted = _delete_resource(repository, remote_id)
                except Exception, exc:
                    LOGGER.error(exc, exc_info=True)
                    ret_d[remote_id] = ret_d[remote_id] = html_mark_error(repr(exc))
                else:
                    ret_d[remote_id] = html_mark_warning(u"This record is deleted.")
                    if deleted:
                        count_deleted_resources += 1
            else:
                raw_xml_record = metadata.getField("raw_xml")
                if not repository.contains(remote_id):
                    resources_to_add[remote_id] = raw_xml_record
                else:
                    resources_to_update[remote_id] = raw_xml_record

        #delete and remove from repo's dict the remaining resources if we harvest the whole collection
        if not (from_ or until or set_):
            resources_to_delete = set(repository.remote_ids()).difference(resources_to_update.keys())
            for remote_id in resources_to_delete:
                deleted = _delete_resource(repository, remote_id, remove=True)
                ret_d[remote_id] = html_mark_warning(u"This record is deleted.")
                if deleted:
                    count_deleted_resources += 1

        #add the resources
        count_added_resources = 0
        for remote_id, raw_xml_record in resources_to_add.iteritems():
            source_url = (header.setSpec()[0] \
                              if (metadata_format in 'metashare' \
                                  and 'META-SHARE' in repository_name) or \
                                  'META-SHARE' in repository_name else None)
            try:
                resource = _add_resource(repository, remote_id, \
                                         metadata_format, raw_xml_record, \
                                         source_url)
            except Exception, exc:
                LOGGER.error(exc, exc_info=True)
                ret_d[remote_id] = html_mark_error(repr(exc))
            else:
                count_added_resources += 1
                resource_name = resource.identificationInfo.get_default_resourceName()
                ret_d[remote_id] = OK_MSG, \
                            repr(resource_name), \
                            resource.storage_object.identifier

        #update resources
        count_updated_resources = 0
        for remote_id, raw_xml_record in resources_to_update.iteritems():
            try:
                resource, updated = _update_resource(repository, remote_id, metadata_format, raw_xml_record)
                if updated:
                    count_updated_resources += 1
                resource_name = resource.identificationInfo.get_default_resourceName()
                ret_d[remote_id] = OK_MSG, \
                            repr(resource_name), \
                            resource.storage_object.identifier
            except Exception, exc:
                LOGGER.error(exc, exc_info=True)
                ret_d[remote_id] = html_mark_error(repr(exc))

        LOGGER.info(u'OAI-PMH: {} resources successfully added.'.format(count_added_resources))
        LOGGER.info(u'OAI-PMH: {} resources successfully updated.'.format(count_updated_resources))
        LOGGER.info(u'OAI-PMH: {} resources successfully deleted.'.format(count_deleted_resources))
    if return_:
        return ret_d


def harvest_from_GUI(kwargs):
    """
    Harvests record(s) from the client's repository.
    """
    base_URL, metadata_format, itemid, from_, until, set_ = \
        get_values(kwargs, ("base_URL", \
                            "metadata_format", \
                            "itemid", \
                            "from_", \
                            "until", \
                            "set_"))
    return harvest(base_URL=base_URL, \
               metadata_format=metadata_format, \
               remote_id=itemid, \
               from_=from_, \
               until=until, \
               set_=set_,\
               return_=True)

#==========================
# Helper functions to harvest resources
#==========================
def _compute_checksum(raw_xml_record):
    checksum = md5()
    checksum.update(raw_xml_record)
    return checksum.hexdigest()

def _get_storage_json(storage_id):
    folder = os.path.join(STORAGE_PATH, storage_id)
    storage_file = open(("{0}/storage-global.json").format(folder))
    # read json string
    storage_json_string = storage_file.read()
    # convert to json object
    storage_json = json.loads(storage_json_string)
    storage_file.close()
    return storage_json

def _convert_to_MSschema(metadataPrefix, raw_xml_record):
    if metadataPrefix == 'olac':
        xslt_fname = 'OLACConverters/olacToMetashare.xsl'
    elif metadataPrefix == 'cmdi':
        xslt_fname = 'CMDIConverters/cmdiToMetashare.xsl'
    else:
        return raw_xml_record
    with open('{}/../misc/tools/{}'.format(ROOT_PATH, xslt_fname)) as f:
        xslt_root = etree.parse(f)
    transform = etree.XSLT(xslt_root)
    xml_root = etree.fromstring(
        raw_xml_record.encode('utf-8'),
        parser=etree.XMLParser(encoding='utf-8', remove_blank_text=True, ns_clean=True),
    )
    metashare_elem = transform(xml_root)
    return etree.tostring(metashare_elem)

def _add_resource(repository, remote_id, metadataPrefix, raw_xml_record, source_url):
    #TODO: copy_status = PROXY or MASTER. If PROXY then source_node=None
    #and source_url the harvested repo's url. If MASTER then source_node= None
    #and source_url= our repo's url
    xml_record = _convert_to_MSschema(metadataPrefix, raw_xml_record)
    # if resource comes from a META-SHARE node, then the imported resource belongs to that
    # repository and it has the same identifer as the remote identifier.
    # Eitherwise the imported resource will have as master META-SHARE node, this node
    resource = (add_or_update_resource(None, xml_record, None, \
                                       source_node=source_url, \
                                       identifier=remote_id, \
                                       publication_status=INGESTED, \
                                       source_url=source_url) \
                if source_url else \
                    import_from_string(xml_record, \
                                       INGESTED, \
                                       MASTER, \
                                       DJANGO_URL))

    checksum = _compute_checksum(raw_xml_record)
    so = resource.storage_object
    repository[remote_id] = [so, checksum]
    return resource

def _update_resource(repository, remote_id, metadataPrefix, raw_xml_record):
    storage_object, checksum = repository[remote_id]
    # Re-compute the checksum of the record and if it is different
    # update the resource
    new_checksum = _compute_checksum(raw_xml_record)
    if checksum == new_checksum:
        resource = storage_object.resourceinfotype_model_set.all()[0]
        return resource, False
    xml_record = _convert_to_MSschema(metadataPrefix, raw_xml_record)
    resource = add_or_update_resource(_get_storage_json(storage_object.identifier), \
                                      xml_record, \
                                      storage_object.digest_checksum, \
                                      copy_status=storage_object.copy_status, \
                                      source_node=storage_object.source_node)
    so = resource.storage_object
    repository[remote_id] = [so, new_checksum]
    return resource, True

def _delete_resource(repository, remote_id, remove=False):
    if repository.contains(remote_id):
        so, _dc = repository[remote_id]
        if remove: # this record is removed from the client's repo, so remove it
            del repository[remote_id]
        so.deleted = True
        so.save()
        # explicitly write metadata XML and storage object to the storage folder
        so.update_storage()
        # update statistics
        saveLRStats(so.resourceinfotype_model_set.all()[0], DELETE_STAT)
        return True
    return False