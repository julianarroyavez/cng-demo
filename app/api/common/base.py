# -*- coding: utf-8 -*-

import falcon

from app.api.common.embed_factory import embed_entity_service_factory
from app.errors import AppError, UnknownError
from app.util.json_util import to_json

try:
    from collections import OrderedDict
except ImportError:
    OrderedDict = dict

from app import log

LOG = log.get_logger()

not_implemented = "Not Implemented"


class BaseResource(object):

    def on_error(self, res, error=UnknownError(description="on_error called with None error")):
        """
        error will be handled by falcon error interceptor i.e. AppError.handle()
        """
        raise error

    def on_success(self, res, status_code=falcon.HTTP_200, body=None):
        res.status = status_code
        res.body = to_json(body)

    def on_image_success(self, res, body=None, content_type=falcon.MEDIA_JPEG):
        res.content_type = content_type
        res.status = falcon.HTTP_200
        res.body = body

    def on_get(self, req, res):
        if req.path == "/":
            raise AppError.from_falcon_error(falcon.HTTPMethodNotAllowed(
                allowed_methods=[]
            ))
        else:
            raise AppError.from_falcon_error(falcon.HTTPNotImplemented(
                title=not_implemented,
                description="GET not implemented for {}".format(req.url))
            )

    def on_post(self, req, res):
        raise AppError.from_falcon_error(falcon.HTTPNotImplemented(
            title=not_implemented,
            description="POST not implemented for {}".format(req.url))
        )

    def on_put(self, req, res):
        raise AppError.from_falcon_error(falcon.HTTPNotImplemented(
            title=not_implemented,
            description="PUT not implemented for {}".format(req.url))
        )

    def on_delete(self, req, res):
        raise AppError.from_falcon_error(falcon.HTTPNotImplemented(
            title=not_implemented,
            description="DELETE not implemented for {}".format(req.url))
        )

    def embed_entities(self, req, res_body,
                       user_extractor=lambda req_body, res_body: req_body.context["auth_claims"].get('user')):
        LOG.info('into embed_entities()')

        if req.get_param('_embed') is None:
            return

        embed_list = req.get_param('_embed').split(",")
        LOG.info(embed_list)

        for entity in embed_list:
            try:
                service_method = embed_entity_service_factory(entity)
                service_method(res_body, user_extractor(req_body=req, res_body=res_body), req.params)
            except Exception as e:
                LOG.error('failed to embed {} with failure {}'.format(entity, e if e is not None else "UNKNOWN_EXCEPTION"))
