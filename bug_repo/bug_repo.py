import os
import re
import json
import nonebot
from nonebot import on_command
from nonebot.permission import SUPERUSER
from nonebot.adapters.cqhttp import Bot
from nonebot.adapters.cqhttp.event import MessageEvent
from nonebot.rule import to_me
from nonebot.typing import T_State

from .Json import readJson, deleteJson, writeJson
from .check import get_group_info, get_user_info_private, get_user_info_group

if not os.path.exists('data/bug_repo_json.json'):
    with open('data/bug_repo_json.json', 'w') as file:
        file.write('[]')

bug_repo_group = nonebot.get_driver().config.bug_repo_group
bug_repo_group_err = nonebot.get_driver().config.bug_repo_group_err

bug_repo = on_command('bug反馈', aliases={'反馈bug'}, rule=to_me(), priority=3)
bug_repo_replay = on_command('bug回复', aliases={'回复反馈', '回复bug'}, permission=SUPERUSER, rule=to_me(), priority=3)
bug_repo_del = on_command('删除反馈', permission=SUPERUSER, rule=to_me(), priority=3)
bug_repo_get = on_command('获取反馈', permission=SUPERUSER, aliases={'反馈列表'}, rule=to_me(), priority=3)
bug_repo_gonggao = on_command('发布公告', aliases={'全服公告'}, permission=SUPERUSER, rule=to_me(), priority=3)

bug_repo.__doc__ = """bug反馈|反馈bug"""


@bug_repo.got("msg", prompt="输入需要反馈的内容")
async def get_msg(bot: Bot, event: MessageEvent, state: T_State):
    user_id = event.user_id
    msg = state["msg"]
    data = readJson()
    repoid = len(data)+1
    if event.message_type == 'group':
        group_id = event.group_id
        group_info = await get_group_info(bot, group_id)
        msg_user_info = await get_user_info_group(bot, group_id, user_id, type=1)
        writeJson(repoid, user_id, msg, group_id, data)
        await bot.call_api('send_group_msg', **{
            'message': f'{group_info}({group_id})的{msg_user_info}({user_id})反馈了:\n'+f'{msg}\n'+f'repoid:{repoid}',
            'group_id': f'{bug_repo_group}'
        })
    elif event.message_type == 'private':
        msg_user_info = get_user_info_private(bot, user_id)
        group_id = '0'
        writeJson(repoid, user_id, msg, group_id, data)
        await bot.call_api('send_group_msg', **{
            'message': f'{msg_user_info}({user_id})反馈了:\n'+f'{msg}\n'+f'repoid:{repoid}',
            'group_id': f'{bug_repo_group}'
        })
    await bug_repo.send(message='反馈成功')


@bug_repo_replay.got('msg_raw', prompt='输入repoid,msg=回复内容')
async def get_repoid(bot: Bot, event: MessageEvent, state: T_State):
    msg_raw = str(state["msg_raw"]).strip()
    msg_re = re.match(r'.*?(.*)(,|，)msg=(.*)', msg_raw, re.M | re.I)
    if msg_re:
        repoid = int(msg_re.group(1))
        send_msg = str(msg_re.group(3))
        data = readJson()
        d1 = []
        num_item = len(data)
        for i in range(num_item):
            repoid1 = data[i]['repoid']
            d1.append(repoid1)
        if repoid in d1:
            for i in range(num_item):
                repoid2 = data[i]['repoid']
                group_id = data[i]['group_id']
                user_id = data[i]['user_id']
                if repoid2 == repoid:
                    await bot.call_api('send_group_msg', **{
                        'message': f'[CQ:at,qq={user_id}]' + f'{send_msg}',
                        'group_id': f'{group_id}'
                    })
                else:
                    pass
            await bug_repo_replay.send(message='发送成功')
        elif repoid not in d1:
            await bug_repo_replay.reject(message='请输入正确的repoid')
    elif msg_re is None:
        await bug_repo_replay.send(message='匹配失败，检查信息')


@bug_repo_del.got('repoid', prompt='输入repoid')
async def del_bugrepo(bot: Bot, event: MessageEvent, state: T_State):
    repoid_raw = int(state["repoid"])
    data = readJson()
    d1 = []
    num_item = len(data)
    if num_item != 0:
        for i in range(num_item):
            repoid1 = data[i]['repoid']
            d1.append(repoid1)
        if repoid_raw in d1:
            deleteJson(repoid_raw, data)
            await bug_repo_del.send(message='删除成功')
        else:
            await bug_repo_del.send(message='请输入正确的repoid')
    else:
        await bug_repo_del.send(message='反馈列表为空')


@bug_repo_get.handle()
async def _(bot: Bot, event: MessageEvent):
    data = readJson()
    num_item = len(data)
    if num_item != 0:
        for i in range(num_item):
            group_id = data[i]['group_id']
            user_id = data[i]['user_id']
            repoid = data[i]['repoid']
            msg_raw = data[i]['msg']
            if group_id == 0:
                user_info = await get_user_info_private(bot, user_id)
                msg = f'repoid:{repoid} {user_info}反馈:\n{msg_raw}\n'
                await bug_repo_get.send(message=f'{msg}')
            elif group_id != 0:
                group_user_info = await get_user_info_group(bot, group_id, user_id, type=1)
                group_info = await get_group_info(bot, group_id)
                msg = f'repoid:{repoid} {group_info}的{group_user_info}反馈:\n{msg_raw}\n'
                await bug_repo_get.send(message=f'{msg}')
    else:
        await bug_repo_del.send(message='反馈列表为空')


@bug_repo_gonggao.got('gonggao', prompt='公告内容')
async def _(bot: Bot, event: MessageEvent, state: T_State):
    msg_raw = state["gonggao"]
    get_group_list = await bot.call_api('get_group_list', **{})
    group_id_list = json.loads(json.dumps(get_group_list))
    num_item = len(group_id_list)
    for i in range(num_item):
        group_id = group_id_list[i]['group_id']
        if group_id not in bug_repo_group_err:
            await bot.call_api('send_group_msg', **{
                'message': f'{msg_raw}',
                'group_id': f'{group_id}'
            })
    await bug_repo_gonggao.send(message='发送成功')
