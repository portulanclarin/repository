# coding=utf-8
from os import path
import saml2
import saml2.saml
BASEDIR = path.dirname(path.abspath(__file__))
CONFIG = {
    # full path to the xmlsec1 binary programm
    'xmlsec_binary': '/usr/bin/xmlsec1',

    # your entity id, usually your subdomain plus the url to the metadata view
    'entityid': 'https://portulanclarin.net/saml2/metadata/',

    # directory with attribute mapping
    'attribute_map_dir': path.join(BASEDIR, 'attributemaps'),

    # this block states what services we provide
    'service': {
        'sp': {
            'name': 'PORTULAN / CLARIN',
            'endpoints': {
                # url and binding to the assertion consumer service view
                # do not change the binding or service name
                'assertion_consumer_service': [
                    ('https://portulanclarin.net/saml2/acs/',
                     saml2.BINDING_HTTP_POST),
                ],
                # url and binding to the single logout service view
                # do not change the binding or service name
                'single_logout_service': [
                    ('https://portulanclarin.net/saml2/ls/',
                     saml2.BINDING_HTTP_REDIRECT),
                    ('https://portulanclarin.net/saml2/ls/post',
                        saml2.BINDING_HTTP_POST),
                ],
            },
            'idp': {
                # This is the address of a SimpleSAMLphp proxy, which acts as the sole IdP
                #  known to this repository and as SP to the CLARIN federation
                'https://sso.portulanclarin.net/saml2/idp/metadata.php': {
                    'single_sign_on_service': {
                        saml2.BINDING_HTTP_REDIRECT: 'https://sso.portulanclarin.net/saml2/idp/SSOService.php',
                    },
                    'single_logout_service': {
                        saml2.BINDING_HTTP_REDIRECT: 'https://sso.portulanclarin.net/saml2/idp/SingleLogoutService.php',
                    },
                },
            },

            # attributes that this project need to identify a user
            'required_attributes': ['uid', 'displayName', 'cn', 'sn'],

            # attributes that may be useful to have but not required
            # 'optional_attributes': ['eduPersonAffiliation'],
        },
    },

    # where the remote metadata is stored
    'metadata': {
        'local': [
            # this file is not included in the repository
            # you should create your own SAML metadata file ;-)
            path.join(BASEDIR, 'saml-portulan-idp.xml'),
        ],
    },

    # set to 1 to output debugging information
    'debug': 1,

    # Signing
    # these files are not included in the repository; you should create your own ;-)
    'key_file': path.join(BASEDIR, 'saml-sp-priv.pem'),
    'cert_file': path.join(BASEDIR, 'saml-sp-pub.pem'),

    'contact_person': [
        {
            'given_name': u'Luís',
            'sur_name': 'Gomes',
            'company': 'University of Lisbon',
            'email_address': 'luis.gomes@di.fc.ul.pt',
            'contact_type': 'technical'
        },
        {
            'given_name': u'António',
            'sur_name': 'Branco',
            'company': 'University of Lisbon',
            'email_address': 'ahb@di.fc.ul.pt',
            'contact_type': 'administrative'
        },
    ],
    'organization': {
        'name': [('PORTULAN / CLARIN -- Infrastructure for Science and Technology of the Portuguese Language', 'en')],
        'display_name': [('PORTULAN / CLARIN', 'en')],
        'url': [('http://portulanclarin.net/', 'en')],
    },
    'valid_for': 24,  # how long is our metadata valid
}
