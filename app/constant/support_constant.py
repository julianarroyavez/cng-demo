GET_ALL_FAQS_QUERY = 'select * from ' \
                     '(select id, content_type, content_text, content_format, additional_text, parent_id, rank ' \
                     'from support.faqs ' \
                     'where content_type in (\'CATEGORY\') ' \
                     'order by rank) as a1 ' \
                     'union all ' \
                     'select * from ' \
                     '(select id, content_type, content_text, content_format, additional_text, parent_id, rank ' \
                     'from support.faqs ' \
                     'where content_type in (\'QUESTION\') ' \
                     'order by rank) as a2 ' \
                     'union all  ' \
                     'select * from ' \
                     '(select id, content_type, content_text, content_format, additional_text, parent_id, rank ' \
                     'from support.faqs ' \
                     'where content_type in (\'ANSWER\', \'ACTION\') ' \
                     'order by rank) as a3;'

GET_COUNT_OF_RAISED_QUERY_WITHIN_24_HOURS = 'select count(1) from support.support_queries ' \
                                            'where customer_phone = \'%s\' ' \
                                            'and created_on <= \'%s\' ' \
                                            'and (created_on + interval \'1440 minute\') >= \'%s\' ;'
