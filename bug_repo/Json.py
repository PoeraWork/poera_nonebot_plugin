import json


def readJson():
    with open(r'data/bug_repo_json.json', 'r') as f_in:
        data = json.load(f_in)
        f_in.close()
        return data


def writeJson(repoid: int, user_id: int, msg: str, group_id: int, data: dict):
    d1 = {}
    d1 = json.loads(json.dumps(d1))
    d1['repoid'] = repoid
    d1['group_id'] = group_id
    d1['user_id'] = user_id
    d1['msg'] = msg
    data.append(d1)
    with open(r'data/bug_repo_json.json', 'w') as f_out:
        json.dump(data, f_out)
        f_out.close()


def deleteJson(repoid: int, data: dict):
    item_list = []
    num_item = len(data)
    for i in range(num_item):
        reid = data[i]['repoid']
        id = len(item_list) + 1
        if reid != repoid:
            group_id = data[i]['group_id']
            user_id = data[i]['user_id']
            msg = data[i]['msg']
            item_dict = {'repoid': id, 'group_id': group_id,
                         'user_id': user_id, 'msg': msg}
            item_list.append(item_dict)
    with open(r'data/bug_repo_json.json', 'w') as f_out:
        json.dump(item_list, f_out)
        f_out.close()
