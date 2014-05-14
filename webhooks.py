from wsgiref.simple_server import make_server
from pprint import pformat, pprint

def application(environ, start_response):
    status = '200 OK'

    #assert False
    response_headers = [('Content-type', 'text/plain')]
    start_response(status, response_headers)
    try:
        length = int(environ.get('CONTENT_LENGTH', '0'))
    except ValueError:
        length = 0

    #print environ['wsgi.input'].read(length)
    output = pformat(environ)    
    return [output]
    
#from paste.evalexception.middleware import EvalException
#application = EvalException(application)

if __name__ == '__main__':
    httpd = make_server('', 8005, application)
    print "server running"
    httpd.handle_request()
