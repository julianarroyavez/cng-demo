from app import config
from app.domain.resource_schema import Units


class SlotDurationService:

    def embed_slot_durations(self, root_body, user_id, params):

        embed_list = []
        duration_list = [int(i) for i in config.DURATION['duration'].split(',')]
        for duration in duration_list:
            embed_list.append({
                "name": "{} Min".format(duration) if duration < 60 else "{} Hour".format(int(duration/60)),  # todo apply correct format logic
                "value": duration,
                "unit": Units.Minute.value
            })

        root_body['_embedded'] = root_body.get('_embedded', {})
        root_body['_embedded']['slotDurations'] = embed_list
