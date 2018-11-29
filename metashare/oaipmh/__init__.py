# coding=utf-8
# pylint:
from collections import OrderedDict
from django.core.urlresolvers import reverse
from oaipmh.server import Server
from oaipmh.metadata import MetadataRegistry

from metashare.oaipmh.oaipmh_server import OaiPmhServer
from metashare.oaipmh.metadata_handlers import MetashareWriter, OlacWriter, CmdiWriter
from metashare.oaipmh._utils import *
from metashare.oaipmh.oaipmh_verbs import (
    harvest_from_GUI, ListIdentifiers, ListRecords, Identify, ListSets, ListMetadataFormats
)

def metadata_registry():
    registry = MetadataRegistry()
    registry.registerWriter('metashare', MetashareWriter())
    registry.registerWriter('olac', OlacWriter())
    registry.registerWriter('cmdi', CmdiWriter())
    return registry

oaipmh_proto_server = OaiPmhServer()

oaipmh_server = Server(
    server=oaipmh_proto_server,
    metadata_registry=metadata_registry(),
    resumption_batch_size=1000,
)

#==========================
# Supported commands
#==========================

supported_commands = OrderedDict()

key_import = u"Import Resource(s)"
supported_commands[key_import] = harvest_from_GUI

key_list_ids_for_import = u"List Identifiers (use for import)"
supported_commands[key_list_ids_for_import] = ListIdentifiers

# available as separate buttons
supported_commands[u"List Records"] = ListRecords
supported_commands[u"Identify Server"] = Identify
supported_commands[u"List Sets"] = ListSets

key_list_metadata_format = u"List Metadata Formats"
supported_commands[key_list_metadata_format] = ListMetadataFormats
