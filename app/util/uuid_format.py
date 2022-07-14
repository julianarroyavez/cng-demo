
def convert_string_without_dashes_to_uuid(uuid_string):
    uuid_string = '-'.join([uuid_string[:8], uuid_string[8:12], uuid_string[12:16],
                            uuid_string[16:20], uuid_string[20:]])
    return uuid_string
