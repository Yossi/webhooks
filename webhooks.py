from wsgiref.simple_server import make_server
from pprint import pformat, pprint
import sys, os
import json
from subprocess import call

# "inspired" by (read, stolen from): https://github.com/logsol/Github-Auto-Deploy

def getConfig():
    try:
        configString = open(os.path.dirname(__file__) + '/config.json').read()
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

def getUrl(environ):
    try:
        length = int(environ.get('CONTENT_LENGTH', '0'))
    except ValueError:
        length = 0

    url = json.loads(environ['wsgi.input'].read(length))['repository']['url']
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


def application(environ, start_response):
    #output = pformat(environ)
    output = 'Thank you, come again'

    for path in getMatchingPaths(getUrl(environ)):
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
