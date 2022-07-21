from app.domain.booking_schema import Slots


class SlotsRepository:
    def fetch_all_by_nozzle_list(self, date, status, nozzle_list_of_station_for_connector_type):
        return Slots.select(
            Slots.nozzle, Slots.start_time, Slots.end_time, Slots.status, Slots.vacancy, Slots.date
        ).where(
            (Slots.date == date)
            & (Slots.status == status)
            & (Slots.nozzle.in_(nozzle_list_of_station_for_connector_type))
        ).order_by(Slots.start_time)

    def fetch_all_by_date(self, date, start_time, end_time):
        return Slots.select(
            Slots.nozzle
        ).where(
            (Slots.date == date) & (Slots.vacancy == 0)
            & (Slots.status == 'BOOKED')
            & (((Slots.start_time <= start_time)
                & (Slots.end_time >= end_time))
               | (Slots.start_time.between(start_time, end_time))
               | ((Slots.end_time > start_time)
                  & (Slots.end_time <= end_time))))

    def insert(self, user_id, nozzle, date, start_time, end_time, status, vacancy):
        return Slots.create(
            created_by=user_id,
            modified_by=user_id,
            nozzle=nozzle.record_id,
            date=date,
            start_time=start_time,
            end_time=end_time,
            slot_number='{:02d}-{:02d}{:02d}'.format(nozzle.record_id, start_time.hour, start_time.minute),
            status=status,
            vacancy=vacancy
        )

    def fetch_by_id(self, slot_id):
        return (Slots.select()
                .where(Slots.id == slot_id).get())

    def update(self, record):
        return record.save()

    def fetch_all_by_nozzle_list_and_slot_time(self, date, status, nozzle_list_of_station_for_connector_type,
                                               start_time, end_time):
        return Slots.select(
            Slots.nozzle, Slots.start_time, Slots.end_time, Slots.vacancy
        ).where(
            (Slots.date == date)
            & (Slots.status == status)
            & (Slots.nozzle.in_(nozzle_list_of_station_for_connector_type))
            & (((Slots.start_time >= start_time) & (Slots.start_time < end_time)) | (
                        (Slots.end_time <= end_time) & (Slots.end_time > start_time)))
        )

    def get_slot_by_nozzle_and_slot_time(self, date, nozzle, start_time, end_time):
        return Slots.select(
            Slots.nozzle, Slots.start_time, Slots.end_time, Slots.id, Slots.vacancy, Slots.slot_number
        ).where(
            (Slots.date == date)
            & (Slots.nozzle == nozzle)
            & (((Slots.start_time >= start_time) & (Slots.start_time < end_time)) | (
                        (Slots.end_time <= end_time) & (Slots.end_time > start_time)))
        )
