from django.http import HttpResponse, HttpResponseRedirect, HttpResponseServerError
from django.core.exceptions import PermissionDenied
from django.shortcuts import render_to_response, get_object_or_404
from django.utils.translation import ugettext as _
from django.utils.http import urlquote
from django.utils.encoding import smart_str
from django.conf import settings
from django.template import RequestContext
from django.db.models import Q

from hgwebproxy.proxy import HgRequestWrapper
from hgwebproxy.utils import is_mercurial, basic_auth
from hgwebproxy.models import Repository
from hgwebproxy import settings as hgwebproxy_settings

from mercurial.hgweb import hgweb
from mercurial import templater

import os

def repo_index(request):
    repo_all = Repository.objects.filter(Q(is_private=False) | Q(owner=request.user))
    return render_to_response("hgwebproxy/repo_all.html", {'repos': repo_all}, 
        RequestContext(request))

def repo_detail(request, username, pattern):
    """
    Repository detail view.
    """

    repo_name = pattern.split('/')[0]
    repo = get_object_or_404(Repository, slug=repo_name, owner__username=username)
    
    """
    Instance the hgweb wrapper
    """
    response = HttpResponse()
    hgr = HgRequestWrapper(request, response, script_name=repo.get_absolute_url())

    """
    Authenticate on all requests. To authenticate only against 'POST'
    requests
    """

    realm = _('Basic auth')

    if is_mercurial(request):
        """
        If a slash is not present, would be added a slash regardless of 
        APPEND_SLASH django setting since hgweb returns 404 if it isn't present.
        """
        if not request.path.endswith('/'):
            new_url = [request.get_host(), request.path + '/']
            if new_url[0]:
                newurl = "%s://%s%s" % (
                    request.is_secure() and 'https' or 'http',
                    new_url[0], urlquote(new_url[1]))
            else:
                newurl = urlquote(new_url[1])
            if request.GET:
                newurl += '?' + request.META['QUERY_STRING']
            return HttpResponseRedirect(newurl)
        
        authed = basic_auth(request, realm, repo)

    else:
        # For web browsers request, Django would handle the permission  
        if not repo.can_browse(request.user):
            raise PermissionDenied(_("You do not have access to this repository"))
        authed = request.user.username

    if not authed:
        response.status_code = 401
        response['WWW-Authenticate'] = '''Basic realm="%s"''' % realm
        return response
    else:
        hgr.set_user(authed)


    hgserve = hgweb(str(repo.location))
    hgserve.reponame = repo.slug

    # TODO: is it Possible to charge the settings just for one time? 
    hgserve.repo.ui.setconfig('web', 'name', smart_str(hgserve.reponame))
    hgserve.repo.ui.setconfig('web', 'description', smart_str(repo.description))
    hgserve.repo.ui.setconfig('web', 'contact', smart_str(repo.owner.get_full_name()))
    hgserve.repo.ui.setconfig('web', 'allow_archive', repo.allow_archive)


    if os.path.exists(hgwebproxy_settings.STYLES_PATH):
        template_paths = templater.templatepath()
        template_paths.insert(0, hgwebproxy_settings.STYLES_PATH)
        hgserve.repo.ui.setconfig('web', 'templates', hgwebproxy_settings.STYLES_PATH)
        hgserve.templatepath = hgserve.repo.ui.config('web', 'templates', template_paths)
    
    if not repo.style == '':
        hgserve.repo.ui.setconfig('web', 'style', repo.style)

    hgserve.repo.ui.setconfig('web', 'baseurl', repo.get_absolute_url())
    hgserve.repo.ui.setconfig('web', 'allow_push', authed) #Allow push to the current user
    hgserve.repo.ui.setconfig('web', 'staticurl', hgwebproxy_settings.STATIC_URL)

    if settings.DEBUG:
        hgserve.repo.ui.setconfig('web', 'push_ssl', 'false')
    else:
        hgserve.repo.ui.setconfig('web', 'push_ssl', repo.allow_push_ssl)

    # Catch hgweb error to show as Django Exceptions
    try:
        response.write(''.join([each for each in hgserve.run_wsgi(hgr)]))
    except KeyError:
        return HttpResponseServerError('Mercurial has crashed', mimetype='text/html')

    context = {
        'content': response.content,
        'reponame' : hgserve.reponame,
        'slugpath': request.path.replace(repo.get_absolute_url(), ''),
        'is_root': request.path == repo.get_absolute_url(),
        'repo': repo,
    }

    return render_to_response("hgwebproxy/wrapper.html", context, RequestContext(request))
