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
        if not os.path.isdir(repository['path']):
            sys.exit('Directory ' + repository['path'] + ' not found')
        if not os.path.isdir(repository['path'] + '/.git'):
            sys.exit('Directory ' + repository['path'] + ' is not a Git repository')

    return config

def getPayload(environ):
    try:
        length = int(environ.get('CONTENT_LENGTH', '0'))
    except ValueError:
        length = 0
    return environ['wsgi.input'].read(length)

def getUrl(payload):
    return json.loads(payload).get('repository', {}).get('url', '')

def HMAC_OK(key, payload, hash):
    computed_hash = hmac.new(key, payload, hashlib.sha1).hexdigest()
    return hash.split('=')[-1] == computed_hash

def application(environ, start_response):
    output = 'Go away'

    config = getConfig()
    hash = environ.get('HTTP_X_HUB_SIGNATURE', '')
    payload = getPayload(environ)
    repoUrl = getUrl(payload)
    
    for repository in config['repositories']:
        key = str(repository.get('key', ' ')) # not unicode, unicode makes HMAC sad
        print key, type(key)
        if repository['url'] == repoUrl and HMAC_OK(key, payload, hash):
            output = 'Thank you, come again!'
            path = repository['path']
            deploy = repository.get('deploy', 'touch deploy_time')
            
            call(['cd "' + path + '" && git fetch --all && git reset --hard origin/master'], shell=True) # pull
            call(['cd "' + path + '" && ' + deploy], shell=True) # deploy

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
