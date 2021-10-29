import json
from nonebot.adapters.cqhttp import Bot


async def get_group_info(bot: Bot, group_id):
    group_info_raw = await bot.call_api('get_group_info', **{
        'group_id': f'{group_id}'
    })
    group_info = json.loads(json.dumps(group_info_raw))
    group_info = group_info['group_name']
    return group_info


async def get_user_info_private(bot: Bot, user_id):
    user_raw = await bot.call_api('get_stranger_info', **{
        'user_id': f'{user_id}'
    })
    user_info = json.loads(json.dumps(user_raw))
    user_info = user_info['nickname']
    return user_info


async def get_user_info_group(bot: Bot, group_id, user_id, type):
    user_info_raw = await bot.call_api('get_group_member_info', **{
        'group_id': f'{group_id}',
        "user_id": f'{user_id}'
    })
    user_info = json.loads(json.dumps(user_info_raw))
    user_info1 = user_info['nickname']
    user_info2 = user_info['role']
    if type == 1:
        return user_info1
    if type == 2:
        if user_info2 in ['owner', 'admin']:
            if user_info2 == 'admin':
                return 1
            elif user_info2 == 'owner':
                return 2
        else:
            return 0
