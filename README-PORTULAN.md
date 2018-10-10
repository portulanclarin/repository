
# Installation on a fresh Ubuntu 16.04 LTS Server

Install python and pyenv:

    curl https://gist.githubusercontent.com/luismsgomes/23d408c53049edc64e2a5b6b838d2fb7/raw/ | bash


# Single Sign-On

To create the certificate for SAML:

    openssl req -newkey rsa:2048 -new -x509 -days 3652 -nodes -keyout saml-sp-priv.pem -out saml-sp-pub.pem

It will ask some questions, which I have answered as follows:

    Country Name (2 letter code) [AU]:PT
    State or Province Name (full name) [Some-State]:Lisboa
    Locality Name (eg, city) []:Lisboa
    Organization Name (eg, company) [Internet Widgits Pty Ltd]:CLARIN / PORTULAN
    Organizational Unit Name (eg, section) []:
    Common Name (e.g. server FQDN or YOUR name) []:clarinportulan.net
    Email Address []:luis.gomes@di.fc.ul.pt

To re-generate the SAML Service Provider metadata (clarinportulan-sp-metadata.xml):

    cd metashare
    make_metadata.py local_settings_saml.py > saml-portulan-sp.xml


To propagate the SAML Service Provider metadata to the CLARIN Federation see instructions at:

    https://github.com/clarin-eric/SPF-SPs-metadata


To download the metadata for all IdPs of CLARIN Federation:

    wget https://infra.clarin.eu/aai/prod_md_about_spf_idps.xml

