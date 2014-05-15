from wsgiref.simple_server import make_server
from pprint import pformat, pprint
import sys, os
import json
from subprocess import call
import hashlib
import hmac

# "inspired" by (read, stolen from): https://github.com/logsol/Github-Auto-Deploy

def getConfig():
    try:
        configString = open(os.path.join(os.path.dirname(__file__), 'config.json')).read()
    except:
        sys.exit('Could not load config.json file')

    try:
        config = json.loads(configString)
    except:
        sys.exit('config.json file is not valid json')

    for repository in config['repositories']:
        if(not os.path.isdir(repository['path'])):
            sys.exit('Directory ' + repository['path'] + ' not found')
        if(not os.path.isdir(repository['path'] + '/.git')):
            sys.exit('Directory ' + repository['path'] + ' is not a Git repository')

    return config

def getPayload(environ):
    try:
        length = int(environ.get('CONTENT_LENGTH', '0'))
    except ValueError:
        length = 0
        
    return environ['wsgi.input'].read(length)

def getUrl(payload):
    url = json.loads(payload).get('repository', {}).get('url', '')
    return url

def getMatchingPaths(repoUrl):
    res = []
    config = getConfig()
    for repository in config['repositories']:
        if(repository['url'] == repoUrl):
            res.append(repository['path'])
    return res

def pull(path):
    call(['cd "' + path + '" && git pull'], shell=True)

def deploy(path):
    config = getConfig()
    for repository in config['repositories']:
        if(repository['path'] == path):
            if 'deploy' in repository:
                 call(['cd "' + path + '" && ' + repository['deploy']], shell=True)
            break

def HMAC_OK(payload, hash):
    key = '123'
    print payload
    computed_hash = hmac.new(key, payload, hashlib.sha1).hexdigest()
    print hash
    print computed_hash
    print hash = computed_hash
    
    return True

def application(environ, start_response):
    output = 'Go away'
    #output = pformat(environ)

    payload = getPayload(environ)
    if HMAC_OK(payload, environ.get('HTTP_X_HUB_SIGNATURE', '')):
        output = 'Thank you, come again!'
        for path in getMatchingPaths(getUrl(payload)):
            pull(path)
            deploy(path)

    status = '200 OK'
    response_headers = [('Content-type', 'text/plain'),
                        ('charset', 'utf-8')]
    start_response(status, response_headers)
    return [output.encode('utf-8')]
    
#from paste.evalexception.middleware import EvalException
#application = EvalException(application)

if __name__ == '__main__':
    httpd = make_server('', 8005, application)
    print "server running"
    httpd.handle_request()
