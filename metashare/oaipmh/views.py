import logging
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.http import HttpResponse
from django.utils.safestring import mark_safe

from metashare.settings import LOG_HANDLER, OAIPMH_URL
from metashare.oaipmh.forms import HarvestForm, ExposeForm
from metashare.oaipmh import oaipmh_server, supported_commands, \
    key_list_ids_for_import, key_import, key_list_metadata_format, \
    time_it, smart_extend
    
# Setup logging support.
LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(LOG_HANDLER)

# @login_required
def harvest(request):
    """
    Renders the OAI-PMH harvesting.
    """
    def mark_obj_as_html_ok(data_dict):
        """ Returns html strings """
        if isinstance(data_dict, dict):
            for key, value in data_dict.iteritems():
                if isinstance(value, basestring):
                    data_dict[key] = mark_safe(value)

    def getverb_from_fastbuttons(form):
        """
        Simplification for the user if another button was clicked than
        the Process button.
        """
        verb = form.cleaned_data['verb']
        for key in form.data.keys():
            if key.startswith("verb_"):
                verb = key.replace("verb_", "")
                break
        return verb

    form = HarvestForm(request.POST or None)
    if form.is_valid():
        data_info = {}
        # find out what to do and then do it
        what_to_do = getverb_from_fastbuttons(form)
        try:
            if what_to_do in supported_commands:
                # call the function associated with the task
                ftor = supported_commands[what_to_do]
                tm, data_dict = time_it(ftor, smart_extend(locals(), \
                                                           form.cleaned_data))
                data_info = {
                    "Item size": len(data_dict),
                    "Time taken": tm,
                }
                mark_obj_as_html_ok(data_dict)
                
                # ok so use javascript if needed
                if key_list_ids_for_import == what_to_do:
                    javascript_for_id = 1
                    import_verb = key_import
                elif key_list_metadata_format == what_to_do:
                    javascript_for_id = 2
            else:
                error_str = u"Invalid command [%s]" % what_to_do
        except Exception, exc:
            LOGGER.error(exc, exc_info=True)
            error_str = repr(exc)
    
    # give it all params together with form params
    params = smart_extend(
        {'form_input': form},
        locals(),
        getattr(form, 'cleaned_data', {}),
    )
    return render_to_response(
        'oaipmh/harvest.html',
        params,
        context_instance=RequestContext(request))

# @login_required
def expose(request):
    """
    Render OAI-PMH expose page
    """
    form = ExposeForm(request.POST or None)
    if form.is_valid():
        # construct the url, that requests to the oai server
        verb = form.cleaned_data['verb']
        success_url = '{}?verb={}'.format(OAIPMH_URL, verb)
        itemid = form.cleaned_data['itemid']
        if itemid:
            success_url += "&identifier={}".format(itemid)
        metadata_str = form.cleaned_data['metadata_str']
        if metadata_str:
            success_url += "&metadataPrefix={}".format(metadata_str)
        from_ = form.cleaned_data['from_']
        if from_:
            success_url += "&from={}".format(from_)
        until = form.cleaned_data['until']
        if until:
            success_url += "&until={}".format(until)
        set_ = form.cleaned_data['set_']
        if set_:
            success_url += "&set={}".format(set_)
        resumptionToken = form.cleaned_data['resumptionToken']
        if resumptionToken:
            success_url += "&resumptionToken={}".format(resumptionToken)
        return redirect(success_url)                
    return render_to_response(
        'oaipmh/expose.html',
        {'form': form},
        context_instance=RequestContext(request))

        
def oaipmh_view(request):
    """
    Renders the response of the OAI-PMH Server
    """
    def get_client_ip(request):
        """
        Tracks the remote IP adress
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    

    request_kw = {}
    verb = (request.GET.get("verb") or request.POST.get("verb"))
    if verb:
        request_kw['verb'] = verb
    metadataPrefix = (request.GET.get("metadataPrefix") or \
                      request.POST.get("metadataPrefix"))
    if metadataPrefix:
        request_kw['metadataPrefix'] = metadataPrefix
    from_ = (request.GET.get("from") or request.POST.get("from"))
    if from_:
        request_kw['from'] = from_
    until = (request.GET.get("until") or request.POST.get("until"))
    if until:
        request_kw['until'] = until
    set_ = (request.GET.get("set") or request.POST.get("set"))
    if set_:
        request_kw['set'] = set_
    identifier = (request.GET.get("identifier") or \
                  request.POST.get("identifier"))
    if identifier:
        request_kw['identifier'] = identifier
    res_token = (request.GET.get("resumptionToken") or \
                 request.POST.get("resumptionToken"))
    if res_token:
        request_kw['resumptionToken'] = res_token
        
    content = oaipmh_server.handleRequest(request_kw)
    return HttpResponse(content=content,
                    status=200,
                    content_type="text/xml")