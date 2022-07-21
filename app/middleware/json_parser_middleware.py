import falcon

from app.errors import InvalidParameterError, InvalidFieldError, FieldErrors, AppError
from app.util.json_util import from_json


class JsonParser(object):

    def process_request(self, req, resp):
        # todo change logic remove multiple if-elif
        if req.content_type is not None:
            if 'application/json' in req.content_type:
                self.capture_json_data(req, req.stream.read())

            elif ('multipart/form-data' in req.content_type) and (('/api/v1/bookings/' in req.url)
                                                                  or ('/api/v1/stations/' in req.url)) \
                    and (req.method == 'POST'):
                self.capture_json_data(req, req.get_param('data', required=True))
                try:
                    req.context['attachmentOne'] = req.get_param('attachmentOne', required=False).file
                except Exception:
                    print('file not found')
                try:
                    req.context['attachmentTwo'] = req.get_param('attachmentTwo', required=False).file
                except Exception:
                    print('file not found')
                try:
                    req.context['attachmentThree'] = req.get_param('attachmentThree', required=False).file
                except Exception:
                    print('file not found')

            elif ('multipart/form-data' in req.content_type) and ('/api/v1/stations' in req.url) \
                    and (req.method == 'POST'):
                self.capture_json_data(req, req.get_param('data', required=True))
                try:
                    req.context['thumbnail-file'] = req.get_param('thumbnail-file', required=True).file
                except Exception:
                    raise InvalidParameterError('No file received')

            elif 'multipart/form-data' in req.content_type:
                self.capture_json_data(req, req.get_param('data', required=True))
                if 'account-type' not in req.params or req.params['account-type'] != 'cngvo':
                    try:
                        req.context['file'] = req.get_param('file', required=True).file
                    except Exception:
                        raise InvalidParameterError(field_errors=[InvalidFieldError(FieldErrors.MultipartFile)])
            else:
                req.context['data'] = None

    def capture_json_data(self, req, json):
        try:
            raw_json = json
        except Exception:
            raise AppError.from_falcon_error(
                falcon.HTTPUnsupportedMediaType(code=86, description="Failed to read JSON"))
        try:
            req.context['data'] = from_json(raw_json)
        except UnicodeDecodeError:
            raise AppError.from_falcon_error(falcon.HTTPUnsupportedMediaType(code=86,
                                                                             description="Cannot be decoded by utf-8"))
        except ValueError:
            raise AppError.from_falcon_error(falcon.HTTPUnsupportedMediaType(code=86,
                                                                             description="Failed to parse Malformed JSON or Cannot be decoded by utf-8"))
