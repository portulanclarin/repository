from django import forms
from metashare.oaipmh import supported_commands

class HarvestForm(forms.Form):
    """
    Settings form for OAI-PMH import.
    """
    base_URL = forms.URLField(label=u"OAI-PMH server URL",
                initial=u"http://www.language-archives.org/cgi-bin/olaca3.pl",
                help_text=u"The OAI-PMH domain name that handles OAI-PMH verbs",)

    verb = forms.ChoiceField(label=u"What to do",
                    choices=[(name, name) for name in supported_commands.keys()],
                    help_text=u"Select OAI-PMH action " \
                    "(fill out item id if applicable)",)

    metadata_format = forms.CharField(
                            label=u"Metadata format",
                            help_text=u"Use list metadata for choices",
                            initial=u"olac",
                            required=False,)

    itemid = forms.CharField(label=u"Record ID",
                    help_text=u"Leave empty for the whole collection or " \
                    "if not applicable",
                    required=False,)
    
    from_ = forms.CharField(label=u"From",
                    help_text=u"Lower bound for datestamp-based selective " \
                    "harvesting. e.g '2011-02-01T12:00:00Z' or '2011-02-01'",
                    required=False,)
    
    until = forms.CharField(label=u"Until",
                    help_text=u"Upper bound for datestamp-based selective " \
                    "harvesting. e.g '2011-02-01T12:00:00Z' or '2011-02-01'",
                    required=False,)
    
    set_ = forms.CharField(label=u"Set",
                    help_text=u"Leave empty for the whole collection or " \
                    "if not applicable",
                    required=False,)
    
    
class ExposeForm(forms.Form):
    """
    Settings form for OAI-PMH import.
    """

    VERBS = (('Identify', 'Identify Server'),
            ('GetRecord', 'Get Record'),
            ('ListIdentifiers', 'List Identifiers'),
            ('ListMetadataFormats', 'List Formats'),
            ('ListRecords', 'List Records'),      
            ('ListSets', 'List Sets'),)
    
    FORMATS = (('', '-----------'),
                ('metashare', 'metashare'),
                ('olac', 'olac'),
                ('cmdi', 'cmdi'))


    verb = forms.ChoiceField(label=u"What to do",
                    choices=VERBS,
                    help_text=u"Select OAI-PMH verb " \
                    "(fill out item identifier if applicable)",)

    metadata_str = forms.ChoiceField(label=u"OAI-PMH metadata format",
                        choices=FORMATS,
                        help_text=u"Select a metadata format if applicable " \
                        "with the specified verb",
                        required=False,)

    itemid = forms.CharField(label=u"Item Identifier",
                    help_text=u"Leave empty for the whole collection or " \
                    "if not applicable",
                    required=False,)
    
    from_ = forms.CharField(label=u"From",
                    help_text=u"Lower bound for datestamp-based selective " \
                    "harvesting. e.g '2011-02-01T12:00:00Z' or '2011-02-01'",
                    required=False,)
    
    until = forms.CharField(label=u"Until",
                    help_text=u"Upper bound for datestamp-based selective " \
                    "harvesting. e.g '2011-02-01T12:00:00Z' or '2011-02-01'",
                    required=False,)
                
    set_ = forms.CharField(label=u"Set",
                    help_text=u"Select a set name to specify set criteria " \
                    "for selective harvesting",
                    required=False,)
    
    resumptionToken = forms.CharField(label=u"Resumption Token",
                    help_text=u"Exclusive argument. " \
                    "It is a token returned by a previous request "\
                    "that issued an incomplete list.",
                    required=False,)