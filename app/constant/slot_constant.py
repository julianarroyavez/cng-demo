slot_count_for_station = 'select floor(extract(hours from sum(sod.operation_end_time - sod.operation_start_time)) + ' \
                         'extract(minutes from sum(sod.operation_end_time - sod.operation_start_time))/60 ' \
                         '- ' \
                         'case when sum(sobd.break_end_time - sobd.break_start_time) is not null then ' \
                         'extract(hours from sum(sobd.break_end_time - sobd.break_start_time)) ' \
                         '+ extract(minutes from sum(sobd.break_end_time - sobd.break_start_time))/60 ' \
                         'else 0 end) ' \
                         'as total_hours, ' \
                         'floor(extract(hours from sum(sod.operation_end_time - (\'%s\'::interval))) + ' \
                         'extract(minutes from sum(sod.operation_end_time + (\'%s\'::interval)))/60) ' \
                         'as remaining_hours ' \
                         'from transactional.station_operation_details sod ' \
                         'left join transactional.station_operation_break_details sobd ' \
                         'on sobd.station_record_id = sod.station_record_id ' \
                         'where sod.station_record_id = \'%s\' ' \
                         'group by sod.operation_end_time, ' \
                         'sod.operation_start_time; '

booking_count_for_available_slots = 'select count(1) from transactional.bookings b ' \
                                    'inner join transactional.slots s on s.id = b.slot_id ' \
                                    'where b.station_record_id = \'%s\'  ' \
                                    'and b.service_date = now()::date ' \
                                    'and s.start_time >= (\'%s\'::interval) ' \
                                    'and b.booking_status in (\'BOOKED\',\'COMPLETED\', \'FULFILLED\');'

booking_count_by_total_duration_hourly = 'select coalesce(round(cast(sum(a.total)/60 as numeric),0),0) from ' \
                                  '(select ' \
                                  'count(1), ' \
                                  'case when extract(minutes from sum(s.end_time - s.start_time)) = 0 then ' \
                                  'extract(hours from sum(s.end_time - s.start_time)) * 60 ' \
                                  'else ' \
                                  'extract(minutes from sum(s.end_time - s.start_time)) end as total ' \
                                  'from transactional.bookings b ' \
                                  'inner join transactional.slots s on s.id = b.slot_id ' \
                                  'where b.station_record_id = \'%s\' ' \
                                  'and b.service_date = (\'%s\'::date)  ' \
                                  'and s.start_time >= (\'%s\'::interval) ' \
                                  'and b.booking_status in (\'BOOKED\',\'COMPLETED\', \'FULFILLED\') ' \
                                  'group by s.end_time, s.start_time) a;'
