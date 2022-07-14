import falcon

from app import log

LOG = log.get_logger()


class RequestLogging(object):

    def process_request(self, req, resp):
        LOG.info('----> Request: %s %s' % (req.method, req.url))
        LOG.debug('Request Headers: %s' % req.headers)
        LOG.debug('Request Params: %s' % req.params)

        LOG.debug('Request Path: %s' % req.path.split('/')[-2:])
        if req.method == 'POST':
            LOG.info('Request Body: %s' % req.context['data'])

    def process_resource(self, req, resp, resource, params):
        pass # empty function is required

    def process_response(self, req, resp, resource, req_succeeded):
        LOG.info('<---- Response: %s' % resp.status)
        LOG.debug('Response Headers: %s' % resp.headers)
        if resp.headers.get('content-type', "application/json") in [falcon.MEDIA_JPEG, falcon.MEDIA_PNG, falcon.MEDIA_GIF]:
            LOG.info('Response Body: didn\'t print the file bytes. Check RequestLogging class if required')
        else:
            LOG.info('Response Body: %s' % resp.body)
