import json


def read_data(file_name):
    # read data from json
    # this part could also in DB
    data = open(file_name, mode="r")  # "data_ac.json"
    data = data.read()

    data = "[" + data[:-1] + "]"

    data = json.loads(data)

    return data


def clean_inspection(data):
    # clean_inspection
    # if this part in DB will be more effective
    f_id = list(set([i["fa_id"] for i in data]))
    raw_fa = []
    for one_id in f_id:
        two_fa = [i for i in filter(lambda x: x["fa_id"] == one_id, data)]
        if len(two_fa) == 1:
            raw_fa.extend(two_fa)
            continue
        final_fa = [i for i in filter(lambda x: x["tf"] != "", two_fa)]
        raw_fa.extend(final_fa)

    return raw_fa

