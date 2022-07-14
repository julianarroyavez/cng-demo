import datetime
import math

from app.domain.resource_schema import Vehicles, VehicleMasters, StationOperationDetails, StationOperationBreakDetails
from app.errors import UnknownError
from app.log import LOG
from app.repository.app_configs_repository import AppConfigRepository
from app.repository.nozzles_repository import NozzlesRepository
from app.repository.slots_repository import SlotsRepository
from app.repository.station_operation_break_repository import StationOperationBreakRepository
from app.repository.station_operation_details_repository import StationOperationDetailsRepository
from app.repository.vehicles_repository import VehiclesRepository
from app.util.datetime_util import to_date, to_time, datetime_now, time_to_mins, min_to_time, \
    to_12_hour_format_with_meridian, to_12_hour_format_without_meridian

slot_time_format_string = "{} - {}"


class SlotService:

    def generate_slots(self, station_id, vehicle_id, date, user_id, rated_power_id):
        rated_power_id = 3  # todo for cng testing
        station_operation_details_repository = StationOperationDetailsRepository()
        app_config_repository = AppConfigRepository()
        station_operation_break_details_repository = StationOperationBreakRepository()
        now = datetime_now()
        slot_durations = app_config_repository.fetch_all_slot_durations(now=now)
        durations_string = list(slot_durations.split(','))
        durations = list(map(int, durations_string))
        slot_break_in_min = app_config_repository.fetch_slot_break(now=now)
        try:
            operation_details = station_operation_details_repository.fetch_by_station_id(station_id=station_id,
                                                                                         now=now,
                                                                                         now_in_datetime=to_date(date))

            if operation_details.operation_start_time == operation_details.operation_end_time:
                end_hour_time = 1440
            else:
                end_hour_time = time_to_mins(operation_details.operation_end_time)

            station_operation_window = range(time_to_mins(operation_details.operation_start_time), end_hour_time)
        except StationOperationDetails.DoesNotExist as e:
            raise UnknownError(raw_exception=e, description='Station not setup properly')

        nozzles_of_station_for_connector_type = self.get_nozzles_of_station_for_connector_type(
            vehicle_id=vehicle_id,
            now=now,
            station_id=station_id,
            rated_power_id=rated_power_id
        )

        nozzle_slot_map = self.get_nozzles_slot_for_booked_slots(
            nozzles_of_station_for_connector_type=nozzles_of_station_for_connector_type,
            station_operation_window=station_operation_window,
            date=date, durations=durations, station_id=station_id, now=now
        )
        # return
        LOG.info('After booked slot check: {}'.format(nozzle_slot_map))
        total_no_of_nozzles = nozzles_of_station_for_connector_type.count()

        nozzle_slot_map = self.get_nozzles_slot_for_passed_slots(
            nozzle_slot_map=nozzle_slot_map,
            station_operation_window=station_operation_window,
            date=date, total_no_of_nozzles=total_no_of_nozzles,
            durations=durations
        )

        LOG.info('After passed slot check: {}'.format(nozzle_slot_map))

        slots_as_windows = []

        for duration in durations:
            nozzle_slot_map[duration] = nozzle_slot_map.get(duration, {})

            running_window_slot_count = -1
            slots = []
            for duration_slot in range(
                    0,
                    math.floor((end_hour_time - station_operation_window.start) / duration)
            ):
                LOG.info("inside duration_slot loop with total no of nozzles: %s" % int(total_no_of_nozzles))
                nozzle_slot_map[duration][duration_slot] = nozzle_slot_map[duration].get(duration_slot, 0) + \
                                                           int(total_no_of_nozzles)

                if running_window_slot_count != nozzle_slot_map[duration][duration_slot]:
                    if running_window_slot_count == -1:
                        LOG.info("init running window count")
                        running_window_slot_count = nozzle_slot_map[duration][duration_slot]
                    elif (running_window_slot_count > 0 and nozzle_slot_map[duration][duration_slot] == 0) \
                            or (running_window_slot_count == 0 and nozzle_slot_map[duration][duration_slot] > 0):
                        LOG.info("when counter changes to {} from {}".format(nozzle_slot_map[duration][duration_slot],
                                                                             running_window_slot_count))

                        slots_as_windows = self.get_if_running_window_changes(slots_as_windows,
                                                                              running_window_slot_count, duration_slot,
                                                                              duration, nozzle_slot_map, slots)
                        slots = []
                        running_window_slot_count = nozzle_slot_map[duration][duration_slot]

                LOG.info("do slot adding work")
                LOG.info(" %s %s %s" % (duration_slot, duration, station_operation_window.start))
                LOG.info(" %s" % math.floor((end_hour_time - station_operation_window.start) / duration))

                duration_with_break = duration
                if duration_slot > 0:
                    duration_with_break = duration + int(slot_break_in_min.value)
                LOG.info("%s" % ((duration_slot * duration_with_break) + station_operation_window.start))
                if ((duration_slot * duration_with_break) + station_operation_window.start) >= 1440:
                    start_time = min_to_time(
                        mins=(((duration_slot * duration_with_break) + station_operation_window.start) - 1440)
                    )
                else:
                    start_time = min_to_time((duration_slot * duration_with_break) + station_operation_window.start)
                try:
                    end_time = min_to_time(
                        (duration_slot * duration_with_break) + station_operation_window.start + duration)
                except Exception:
                    end_time = min_to_time(0)

                try:
                    slot_breaks = station_operation_break_details_repository.fetch_all_by_station_id(
                        station_id=station_id,
                        now=now,
                        now_in_datetime=to_date(
                            date))
                except StationOperationBreakDetails.DoesNotExist as e:
                    LOG.info('No breaks found for station with id {} with exception {}', station_id, e)

                if not slot_breaks:
                    self.append_available_slots(slots, start_time, end_time)
                else:
                    for slot_break in slot_breaks:
                        if not slot_break.break_start_time <= start_time < slot_break.break_end_time and \
                                not slot_break.break_start_time < end_time <= slot_break.break_end_time:
                            self.append_available_slots(slots, start_time, end_time)

            slots_as_windows = self.handle_end_scenario(slots, running_window_slot_count, duration, nozzle_slot_map,
                                                        slots_as_windows, duration_slot)

        return slots_as_windows

    def generate_slot_for_booking(self, nozzle, booking_req, user):
        slots_repository = SlotsRepository()

        start_time = to_time(booking_req['slot']['startTime'])
        end_time = to_time(booking_req['slot']['endTime'])

        return slots_repository.insert(user_id=user.record_id, nozzle=nozzle, date=to_date(booking_req['serviceDate']),
                                       start_time=start_time, end_time=end_time, status='BOOKED')

    def get_nozzles_of_station_for_connector_type(self, vehicle_id, now, station_id, rated_power_id):
        vehicles_repository = VehiclesRepository()
        nozzles_repository = NozzlesRepository()
        columns = [Vehicles.record_id, VehicleMasters.charging_connector_records]
        vehicle = vehicles_repository.fetch_by_id(columns=columns, record_id=vehicle_id, now=now)

        nozzles_of_station_for_connector_type = nozzles_repository.fetch_all_by_station_power_and_connector_type(
            now=now,
            station_id=station_id,
            vehicle=vehicle,
            rated_power_id=rated_power_id)

        return nozzles_of_station_for_connector_type

    def get_nozzles_slot_for_booked_slots(self, nozzles_of_station_for_connector_type, date, durations,
                                          station_operation_window, station_id, now):

        slots_repository = SlotsRepository()

        booked_slots = slots_repository.fetch_all_by_nozzle_list(date=to_date(date), status='BOOKED',
                                                                 nozzle_list_of_station_for_connector_type=nozzles_of_station_for_connector_type)

        total_no_of_nozzles = nozzles_of_station_for_connector_type.count()

        LOG.info('total_no_of_nozzles: {}'.format(int(total_no_of_nozzles)))
        nozzle_slot_map = {}
        for slot in booked_slots:
            LOG.info(type(slot.start_time))

            LOG.info('found slot {} - {}'.format(slot.start_time, slot.end_time))

            slot_range = self.create_slot_range(start_time=slot.start_time, start_win=station_operation_window.start)
            LOG.info('***********************^^^^ %s %s' % (slot_range, station_operation_window.start))

            booked_slots_count = slots_repository.fetch_all_by_nozzle_list_and_slot_time(
                date=to_date(date),
                status='BOOKED',
                nozzle_list_of_station_for_connector_type=nozzles_of_station_for_connector_type,
                start_time=slot.start_time,  # slot_range['start_time'], #
                end_time=slot.end_time  # slot_range['end_time'], #
            )

            for duration in durations:

                LOG.info('slots {} - {}'.format(booked_slots_count, total_no_of_nozzles))

                if booked_slots_count == total_no_of_nozzles:
                    slot_range = math.ceil((time_to_mins(slot.end_time) - station_operation_window.start) / duration)
                else:
                    slot_range = math.floor((time_to_mins(slot.end_time) - station_operation_window.start) / duration)

                # Test
                nozzle_slot_map[duration] = nozzle_slot_map.get(duration, {})

                for booked_duration in range(
                        math.floor((time_to_mins(slot.start_time) - station_operation_window.start) / duration),
                        slot_range
                ):
                    nozzle_slot_map[duration][booked_duration] = nozzle_slot_map[duration].get(booked_duration, 0) - 1
        LOG.info('After booked slot check: {}'.format(nozzle_slot_map))
        return nozzle_slot_map

    def get_nozzles_slot_for_passed_slots(self, nozzle_slot_map, date, durations,
                                          station_operation_window, total_no_of_nozzles):
        if to_date(date) == datetime.date.today():
            now_in_min = time_to_mins(datetime.datetime.now().time())
            if not (now_in_min < station_operation_window.start):
                for duration in durations:
                    nozzle_slot_map[duration] = nozzle_slot_map.get(duration, {})
                    valid_start = 0
                    valid_end = min(
                        math.floor((now_in_min - station_operation_window.start) / duration) + 1,
                        math.floor((station_operation_window.stop - station_operation_window.start) / duration)
                    )
                    for passed_slot in range(valid_start, valid_end):
                        nozzle_slot_map[duration][passed_slot] = -int(total_no_of_nozzles)

        return nozzle_slot_map

    def handle_end_scenario(self, slots, running_window_slot_count, duration, nozzle_slot_map, slots_as_windows,
                            duration_slot):

        window_start = to_time(slots[0]['startTime'])
        window_end = to_time(slots[-1]['endTime'])
        LOG.info("OUTSIDE | %s for slot %s in duration %s with running_window_count as %s in %s" % (
            ("AVAILABLE" if running_window_slot_count > 0 else "UNAVAILABLE"), duration_slot, duration,
            running_window_slot_count, nozzle_slot_map[duration]))
        slots_as_windows.append({
            "slotWindow": slot_time_format_string.format(
                to_12_hour_format_without_meridian(time=window_start),
                to_12_hour_format_with_meridian(time=window_end)),
            "status": "AVAILABLE" if running_window_slot_count > 0 else "UNAVAILABLE",
            "durations": [{
                "name": "{} Mins".format(duration) if duration < 60 else "{} Hour".format(
                    int(duration / 60)),
                "value": duration,
                "unit": "MINUTE",
                "slots": slots
            }]
        })

        return slots_as_windows

    def get_if_running_window_changes(self, slots_as_windows, running_window_slot_count, duration_slot, duration,
                                      nozzle_slot_map, slots):

        window_start = to_time(slots[0]['startTime'])
        window_end = to_time(slots[-1]['endTime'])
        LOG.info("inside if running window change")
        LOG.info("%s for slot %s in duration %s with running_window_count as %s in %s" % (
            ("AVAILABLE" if running_window_slot_count > 0 else "UNAVAILABLE"), duration_slot, duration,
            running_window_slot_count, nozzle_slot_map[duration]))
        slots_as_windows.append({
            "slotWindow": slot_time_format_string.format(
                to_12_hour_format_without_meridian(time=window_start),
                to_12_hour_format_with_meridian(time=window_end)),
            "status": "AVAILABLE" if running_window_slot_count > 0 else "UNAVAILABLE",
            "durations": [{
                "name": "{} Mins".format(duration) if duration < 60 else "{} Hour".format(
                    int(duration / 60)),
                "value": duration,
                "unit": "MINUTE",
                "slots": slots
            }]
        })
        LOG.info("window added now clear the things")
        return slots_as_windows

    def append_available_slots(self, slots, start_time, end_time):
        LOG.info("for {} and {}".format(start_time, end_time))
        slots.append({
            "name": "{} - {}".format(
                to_12_hour_format_without_meridian(time=start_time),
                to_12_hour_format_with_meridian(time=end_time)),
            "startTime": start_time.isoformat(),
            "endTime": end_time.isoformat()
        })

    def generate_available_and_unavailable_slots_for_stations(self, station_id):
        station_operation_details_repository = StationOperationDetailsRepository()
        app_config_repository = AppConfigRepository()
        station_operation_break_details_repository = StationOperationBreakRepository()
        now = datetime_now()
        slot_durations = app_config_repository.fetch_all_slot_durations(now=now)
        durations_string = list(slot_durations.split(','))
        durations = list(map(int, durations_string))
        try:
            operation_details = station_operation_details_repository.fetch_by_station_id(station_id=station_id,
                                                                                         now=now,
                                                                                         now_in_datetime=to_date(now))

            if operation_details.operation_start_time == operation_details.operation_end_time:
                end_hour_time = 1440
            else:
                end_hour_time = time_to_mins(operation_details.operation_end_time)

            station_operation_window = range(time_to_mins(operation_details.operation_start_time), end_hour_time)
        except StationOperationDetails.DoesNotExist as e:
            raise UnknownError(raw_exception=e, description='Station not setup properly')

        nozzles_of_station_for_connector_type = self.get_nozzles_of_station(
            now=now,
            station_id=station_id
        )

        nozzle_slot_map = self.get_nozzles_slot_for_booked_slots(
            nozzles_of_station_for_connector_type=nozzles_of_station_for_connector_type,
            station_operation_window=station_operation_window,
            date=now, durations=durations, station_id=station_id, now=now
        )

        total_no_of_nozzles = nozzles_of_station_for_connector_type.count()

        nozzle_slot_map = self.get_nozzles_slot_for_passed_slots(
            nozzle_slot_map=nozzle_slot_map,
            station_operation_window=station_operation_window,
            date=now, total_no_of_nozzles=total_no_of_nozzles,
            durations=durations
        )

        LOG.info('After passed slot check: {}'.format(nozzle_slot_map))

        slots_as_windows = []

        for duration in durations:
            nozzle_slot_map[duration] = nozzle_slot_map.get(duration, {})

            running_window_slot_count = -1
            slots = []
            for duration_slot in range(
                    0,
                    math.floor((end_hour_time - station_operation_window.start) / duration)
            ):
                LOG.info("inside duration_slot loop with total no of nozzles: %s" % int(total_no_of_nozzles))
                nozzle_slot_map[duration][duration_slot] = nozzle_slot_map[duration].get(duration_slot, 0) + \
                                                           int(total_no_of_nozzles)

                if running_window_slot_count != nozzle_slot_map[duration][duration_slot]:
                    if running_window_slot_count == -1:
                        LOG.info("init running window count")
                        running_window_slot_count = nozzle_slot_map[duration][duration_slot]
                    elif (running_window_slot_count > 0 and nozzle_slot_map[duration][duration_slot] == 0) \
                            or (running_window_slot_count == 0 and nozzle_slot_map[duration][duration_slot] > 0):
                        LOG.info("when counter changes to {} from {}".format(nozzle_slot_map[duration][duration_slot],
                                                                             running_window_slot_count))

                        slots_as_windows = self.get_if_running_window_changes(slots_as_windows,
                                                                              running_window_slot_count, duration_slot,
                                                                              duration, nozzle_slot_map, slots)
                        slots = []
                        running_window_slot_count = nozzle_slot_map[duration][duration_slot]

                LOG.info("do slot adding work")
                start_time = min_to_time((duration_slot * duration) + station_operation_window.start)
                try:
                    end_time = min_to_time((duration_slot * duration) + station_operation_window.start + duration)
                except Exception:
                    end_time = min_to_time(0)

                try:
                    slot_breaks = station_operation_break_details_repository.fetch_all_by_station_id(
                        station_id=station_id,
                        now=now,
                        now_in_datetime=to_date(
                            now))
                except StationOperationBreakDetails.DoesNotExist as e:
                    LOG.info('No breaks found for station with id {} with exception {}', station_id, e)

                if not slot_breaks:
                    self.append_available_slots(slots, start_time, end_time)
                else:
                    for slot_break in slot_breaks:
                        if not slot_break.break_start_time <= start_time < slot_break.break_end_time and \
                                not slot_break.break_start_time < end_time <= slot_break.break_end_time:
                            self.append_available_slots(slots, start_time, end_time)

            slots_as_windows = self.handle_end_scenario(slots, running_window_slot_count, duration, nozzle_slot_map,
                                                        slots_as_windows, duration_slot)
        return slots_as_windows

    def get_nozzles_of_station(self, vehicle_id, now, station_id, rated_power_id=None):
        vehicles_repository = VehiclesRepository()
        nozzles_repository = NozzlesRepository()
        columns = [Vehicles.record_id, VehicleMasters.charging_connector_records]
        vehicle = vehicles_repository.fetch_by_id(columns=columns, record_id=vehicle_id, now=now)
        LOG.info('Vehicle data: %s' % vehicle)

        nozzles_of_station_for_connector_type = nozzles_repository.fetch_all_by_station(
            now=now,
            station_id=station_id,
        )

        return nozzles_of_station_for_connector_type

    def create_slot_range(self, start_time, start_win):

        start_min = time_to_mins(start_time)
        start_win_hour = start_win + 30

        start = min_to_time(mins=start_min)
        end = min_to_time(mins=(start_min + 60))

        if start_min % start_win == 0 and start_min % start_win_hour == 30:
            start = min_to_time(mins=start_min)
            end = min_to_time(mins=(start_min + 60))

        elif start_min % start_win == 15 and start_min % start_win_hour == 45:
            start = min_to_time(mins=(start_min - 15))
            end = min_to_time(mins=(start_min + 45))

        elif start_min % start_win == 15 and start_min % start_win_hour == 15:
            start = min_to_time(mins=(start_min - 45))
            end = min_to_time(mins=(start_min + 15))

        return {
            "start_time": start,
            "end_time": end
        }


# return overlap range for two range objects or None if no ovelap
# does not handle step!=1
def range_intersect(r1, r2):
    return range(max(r1.start, r2.start), min(r1.stop, r2.stop)) or None
