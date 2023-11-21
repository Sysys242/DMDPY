from modules.utils import Utils
from websocket     import WebSocket
from time          import sleep, time
from json          import dumps, loads

logger = Utils.get_logger()
config = Utils.get_config(True)

def scrapping_task():
    token = logger.delay_input('Please enter the token to scrap on: ')
    gId = logger.delay_input('Please enter the guild id to scrap on: ')
    cId = logger.delay_input('Please enter the channel id to scrap on: ')

    ws = WebSocket()
    ws.connect('wss://gateway.discord.gg/?v=9&encoding=json')

    ws.send(
        dumps(
            {"op":2,"d":{"token": token,"capabilities":8189,"properties":{"os":"Windows","browser":"Chrome","device":"","system_locale":"fr-FR","browser_user_agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36","browser_version":"113.0.0.0","os_version":"10","referrer":"","referring_domain":"","referrer_current":"","referring_domain_current":"","release_channel":"stable","client_build_number":201332,"client_event_source":None},"presence":{"status":"online","since":0,"activities":[],"afk":False},"compress":False,"client_state":{"guild_versions":{},"highest_last_message_id":"0","read_state_version":0,"user_guild_settings_version":-1,"user_settings_version":-1,"private_channels_version":"0","api_code_version":0}}}
        )
    )
    ws.recv()

    ws.send('{"op":4,"d":{"guild_id":null,"channel_id":null,"self_mute":true,"self_deaf":false,"self_video":false}}')
    ws.recv()

    finished = False
    index = 0
    scrapped = []
    ids = []

    ws.send(dumps({
        "op": 14,
        "d": {
            "guild_id": gId,
            "typing": True,
            "threads": True,
            "activities": True,
        }
    }))
    try:
        while not finished:
            x = []
            if index == 0:
                x = [[0, 99]]
            elif index == 1:
                x = [[0, 99], [100, 199]]
            elif index == 2:
                x = [[0, 99], [100, 199], [200, 299]]
            else:
                x = [[0, 99], [100, 199], [index * 100, (index * 100) + 99]]

            ws.send(dumps({
                "op":14,
                "d":{
                    "guild_id": gId,
                    "channels":{
                        cId:x,
                    }
                }
                }))
            while True:
                resp = loads(ws.recv())
                if resp['t'] == "GUILD_MEMBER_LIST_UPDATE":
                    break
            if resp['t'] == "GUILD_MEMBER_LIST_UPDATE":
                for op in resp['d']['ops']:
                    try:
                        if len(op['items']) == 0 and op['op'] == "SYNC":
                            finished = True
                    except:
                        pass

                for op in resp['d']['ops']:
                    if op['op'] == "SYNC":
                        for item in op['items']:
                            if not "group" in item:
                                try:
                                    if item['member']['user']['discriminator'] == '0':
                                        scrapped.append(item["member"]['user']['username'] + "#null")
                                    else:
                                        scrapped.append(item["member"]['user']['username'] + "#" + item['member']['user']['discriminator'])
                                    ids.append(item["member"]['user']['id'])
                                except Exception as e:
                                    print(e)
                                    print(item)

                logger.success(f'Scrapped Member | Index: {index} | Scrapped Amount: {len(scrapped)}')
                Utils.set_title({
                    'Module': 'Member Scrapper',
                    'Index': str(index),
                    'Scrapped': str(len(scrapped))
                }, time())
                
            index += 1
            sleep(Utils.get_config(True)['scrapper']['dellay']/1000)
    except Exception as e:
       logger.error(str(e))
    ws.close()
    logger.success(f"Finished Scrapping | Scrapped: {len(scrapped)}")
    logger.debug(f"Writting id to the users.txt file...")
    with open('input/users.txt', 'w', encoding="latin-1", errors="ignore") as f:
        for id in scrapped:
            f.write(f'\n{id}')
        f.close()
    with open('input/ids.txt', 'w', encoding="latin-1", errors="ignore") as f:
        for id in ids:
            f.write(f'\n{id}')
        f.close()
    logger.success('Finished scrapping jobs, exported ids & users, press enter to get back to main menu !')
    input('')
    Utils.set_title({
        'Module': 'Main Menu'
    }, time())