import re
from django.contrib.auth import authenticate
from django.core.handlers.wsgi import WSGIRequest
from django.core.handlers.modpython import ModPythonRequest

def is_mercurial(request):
    """
    User agent processor to determine whether the incoming
    user is someone using a browser, or a mercurial client

    In order to qualify as a mercurial user they must have a user
    agent value that starts with mercurial and an Accept header that
    starts with application/mercurial. This guarantees we only force
    those who are actual mercurial users to use Basic Authentication
    """
    agent = re.compile(r'^(mercurial).*')
    accept = request.META.get('HTTP_ACCEPT', None)
    result = agent.match(request.META.get('HTTP_USER_AGENT', ""))

    if result and accept.startswith('application/mercurial-'):
        return True
    else:
        return False

def basic_auth(request, realm, repo):
    """
    Very simple Basic authentication handler
    """

    if request.user.is_authenticated():
        user = request.user
        username = request.user.username
    else:
        auth_string = request.META.get('HTTP_AUTHORIZATION')
        
        if auth_string is None or not auth_string.startswith("Basic"):
            return False

        _, basic_hash = auth_string.split(' ', 1)
        username, password = basic_hash.decode('base64').split(':', 1)
        user = authenticate(username=username, password=password)

    if user:
        if request.method == "POST":
            if repo.can_push(user):
                return username
        else:
            if repo.can_pull(user):
                return username

    return False

def drain_request(request):
    """ Drains post data from request object """
    # it's not very nice to handle this so specifically but I feel we have to
    # using request.raw_post_data can leave us with huge python processes. (>1gb)
    
    if isinstance(request, ModPythonRequest):
        req = request._req
        BUFFER = 64*1024
        while (True):
            s = req.read(BUFFER)
            if not s:
                break
    elif isinstance(request, WSGIRequest):
        inp = request.environ['wsgi.input']
        try:
            content_length = int(request.environ.get('CONTENT_LENGTH', 0))
        except (ValueError, TypeError):
            content_length = 0
        for s in util.filechunkiter(inp, limit=content_length):
            pass
    else:
        # fallback
        raw_post_data = request.raw_post_data
        del raw_post_data

