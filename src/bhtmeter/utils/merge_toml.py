def merge_toml(dict1: dict, dict2: dict) -> dict:
    dict3 = {}
    for k1 in dict1:
        v1 = dict1.get(k1)
        if k1 not in dict2:
            dict3.update({k1: v1})
            continue
        v2 = dict2.pop(k1)
        if type(v1) == dict and type(v2) == dict:
            v1 = merge_toml(v1, v2)
        elif type(v1) == list and type(v2) == list:
            v1.extend(v2)
        elif type(v1) == list:
            v1.append(v2)
        elif type(v2) == list:
            v1 = [v1]
            v1.extend(v2)
        elif v1 == v2:
            pass
        else:
            v1 = [v1, v2]
        dict3.update({k1: v1})
    dict3.update(dict2)
    return dict3
