
def mapper(request_data, mapper):
    mapped_dict = {}

    for key, value in mapper.items():
        _dict = {}
        for json_key in value.split('.'):
            if not _dict:
                _dict = request_data.get(json_key)
            else:
                _dict = _dict.get(json_key)
        else:
            if _dict:
                mapped_dict[key] = _dict

    return mapped_dict
