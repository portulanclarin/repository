
import requests
from django.conf import settings
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from .models import resourceInfoType_model
from metashare.storage.models import StorageObject

# local_settings.py should contain the following three variables:
# EPIC_URL = "URL FOR EPIC API"
# EPIC_USER = "EPIC API USER"
# EPIC_PASS = "EPIC API PASSWORD"


# function add_pid_to_resource(rid) should be called once for every resource
def add_pid_to_resource(rid):
    """rid is the resource id in the repository DB"""
    resource = get_resource(rid)
    url = get_resource_url(resource)
    pid = generate_pid(url)
    set_resource_pid(resource, pid)


def get_resource_url(resource):
    return settings.DJANGO_URL + resource.get_absolute_url()


def get_resource(rid):
    return get_object_or_404(resourceInfoType_model, id=rid)


class PidGenerationException(Exception):
    def __init__(self, message):
        super(PidGenerationException, self).__init__()
        self.message = message


def generate_pid(url):
    """url is the URL to the resource detail view in the repository"""
    req = requests.post(
        "%s/%s" % (settings.EPIC_HOST, settings.EPIC_PREF),
        auth=(settings.EPIC_USER, settings.EPIC_PASS),
        json=[{'type': 'URL', 'parsed_data': url}],
        # we will get a redirect but we don't need to follow it:
        allow_redirects=False,
    )
    # Ensure that we got HTTP 201 Created
    if req.status_code != 201:
        raise PidGenerationException(
            "Got HTTP code %d; expected 201" % req.status_code
        )
    # PID URL is returned in the "Location" header
    pid_url = req.headers.get("Location", None)
    if pid_url is None:
        raise PidGenerationException("Missing Location HTTP header")

    if not pid_url.startswith(settings.EPIC_HOST):
        raise PidGenerationException("Generated PID URL does not begin with configured EPIC_HOST")

    return pid_url[len(settings.EPIC_HOST) + 1:]


def set_resource_pid(resource, pid):
    resource.identificationInfo.identifier = [pid]
    resource.identificationInfo.save()


def create_pids_for_resources():
    for resource in resourceInfoType_model.objects.all():
        if not resource.identificationInfo.identifier:
            add_pid_to_resource(resource.id)
