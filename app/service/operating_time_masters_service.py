import datetime

from app.repository.operating_time_masters_repository import OperatingTimeMasterRepository
from app.util.datetime_util import datetime_now, to_12_hour_format_without_meridian, to_12_hour_format_with_meridian


class OperatingTimeMastersService:
    def embed_operating_time_masters(self, root_body, user_id, params):
        start_times = []
        end_times = []
        operating_time_masters_repository = OperatingTimeMasterRepository()

        operation_start_time_master = operating_time_masters_repository.fetch_all(now=datetime_now(),
                                                                                  operation_type='OPERATION_START')
        operation_end_time_master = operating_time_masters_repository.fetch_all(now=datetime_now(),
                                                                                operation_type='OPERATION_END')

        start_time_duration = operation_start_time_master.duration.seconds
        end_time_duration = operation_end_time_master.duration.seconds

        start_time = str(operation_start_time_master.window_start_time)
        start_time = datetime.datetime.strptime(start_time, "%H:%M:%S")

        end_time = str(operation_end_time_master.window_start_time)
        end_time = datetime.datetime.strptime(end_time, "%H:%M:%S")

        while start_time.time() <= operation_start_time_master.window_end_time:
            start_times.append({
                "name": "{}".format(to_12_hour_format_with_meridian(time=start_time.time())),
                "time": "{}".format(start_time.time())
            })
            start_time = start_time + datetime.timedelta(seconds=start_time_duration)

        while (end_time.time() <= operation_end_time_master.window_end_time) and \
                not(end_time.time() < operation_end_time_master.window_start_time):
            end_times.append({
                "name": "{}".format(to_12_hour_format_with_meridian(time=end_time.time())),
                "time": "{}".format(end_time.time())
            })
            end_time = end_time + datetime.timedelta(seconds=end_time_duration)

        operating_time_masters_dict = {
            "operationStart": {
                "timeWindow": "{} - {}".format(to_12_hour_format_without_meridian(time=operation_start_time_master.window_start_time),
                                               to_12_hour_format_with_meridian(time=operation_start_time_master.window_end_time)),
                "startTime": operation_start_time_master.window_start_time,
                "endTime": operation_start_time_master.window_end_time,
                "times": start_times
            },
            "operationEnd": {
                "timeWindow": "{} - {}".format(to_12_hour_format_without_meridian(time=operation_end_time_master.window_start_time),
                                               to_12_hour_format_with_meridian(time=operation_end_time_master.window_end_time)),
                "startTime": operation_end_time_master.window_start_time,
                "endTime": operation_end_time_master.window_end_time,
                "times": end_times
            }
        }

        if root_body.get('_embedded', None) is None:
            root_body['_embedded'] = {
                'operatingTimeMasters': operating_time_masters_dict
            }
        else:
            root_body['_embedded']['operatingTimeMasters'] = operating_time_masters_dict
        return root_body
