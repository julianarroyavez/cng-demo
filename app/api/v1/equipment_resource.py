import falcon

from app.api.common import BaseResource
from app.errors import AppError, UnknownError
from app.service.equipment_service import EquipmentService


class BulkCollection(BaseResource):
    def on_post(self, req, res):
        try:
            service = EquipmentService()
            body = service.equipments_addition(req_body=req.context['data'], req_auth_claims=req.context['auth_claims'])
            self.on_success(res, status_code=falcon.HTTP_201, body=body)
        except Exception as e:
            self.on_error(res, e if isinstance(e, AppError) else UnknownError(description='failed to add equipments',
                                                                              raw_exception=e))


class ItemIconImage(BaseResource):
    def on_get(self, req, res, icon_id):
        try:
            service = EquipmentService()
            body = service.get_icon_image(icon_id=icon_id, size=req.params.get('size', None))

            self.on_image_success(res=res, body=body, content_type=falcon.MEDIA_PNG)
        except Exception as e:
            self.on_error(res, e if isinstance(e, AppError) else UnknownError(
                description='failed to get equipment-type-masters Icon', raw_exception=e))
