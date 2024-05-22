from modules.discord import Discord
from modules.solver  import Solver
from modules.utils   import Utils
from threading       import Thread
from random          import choice
from base64          import b64encode
from httpx           import get
from time            import sleep, time
from json            import dumps

logger = Utils.get_logger()

tokens_file = Utils.get_file('input/tokens.txt')
proxies_file = Utils.get_file('input/proxies.txt')
config = Utils.get_config(True)

solver = Solver(
    config['captcha']['key'],
    config['captcha']['service'],
)

def joining_task():
    invite = logger.delay_input('Please enter your invite code [discord.gg/**code**]: ')

    logger.clear()
    logger.print_banner('Starting joining job!')
    global sucesss, failed, captcha
    global finished, tokens

    sucesss, failed, captcha = 0, 0, 0
    finished = False

    tokens = tokens_file.get_lines(True)
    proxies = proxies_file.get_lines(True)

    def title_thread():
        global sucesss, failed, captcha
        global finished, tokens
        tokens_len = len(tokens)
        timestamp = time()
        while not finished:
            Utils.set_title({
                'Module': 'Joiner',
                'Sent': sucesss,
                'Captcha': captcha,
                'Failed': failed,
                'Total': f'{tokens_len-len(tokens)}/{tokens_len}',
                'Token Left': len(tokens)
            }, timestamp)

    def joining_thread(unformatted_token:str, info:list, proxy:str):
        global sucesss, failed, captcha
        global added
        added = 0

        token = Utils.get_token_from_str(unformatted_token)
        while True:
            try:
                discord = Discord(token, proxy)
                break
            except Exception as e:
                logger.error(f'{token[:-10]}********** {e}')
        #discord.connect_to_ws()

        finished = False
        tried = 0
        rqtoken = None
        captcha_key = None
        while not finished:
            response = discord.join_server(
                invite=info[0],
                context=info[1],
                rqtoken=rqtoken,
                captcha_key=captcha_key,
                tries=tried
            )
            match response:
                case True:
                    finished = True
                    logger.success(f'{token[:-10]}********** Joined {info[0]}')                    
                case _:
                    if 'rate_limited' in response:
                        time_to_sleep = int(response.split('rate_limited_')[1])
                        logger.info(f'{token[:-10]}********** Sleeping {time_to_sleep} and retrying...')
                        sleep(time_to_sleep)
                    elif 'captcha_solve' in response:
                        _captcha_key = solver.solve(proxy, 'a9b5fb07-92ff-493f-86fe-352a2803b3df', response.split('_')[3])
                        if _captcha_key != 'not_solving':
                            if _captcha_key == "error":
                                logger.error(f'{token[:-10]}********** Failed to solve captcha!')
                            else:
                                rqtoken = response.split('_')[2]
                                captcha_key = _captcha_key  
                        else:
                            finished = True
                            logger.error(f'{token[:-10]}********** Failed to join {info[0]}: captcha_failed')
                        tried += 1
                    else:
                        finished = True
                        logger.error(f'{token[:-10]}********** Failed to join {info[0]}: {response}')
        
    thread_list = []
    Thread(target=title_thread).start()

    context = get(f'https://discord.com/api/v9/invites/{invite}?with_counts=true&with_expiration=true')
    if context.status_code == 200:
        guildId = context.json()['guild']['id']
        channelId = context.json()['channel']['id']
        context = b64encode(dumps({"location":"Join Guild","location_guild_id":guildId,"location_channel_id":channelId,"location_channel_type":0}, separators=(',', ':')).encode()).decode()
    elif context.status_code == 429:
        logger.error('Rate limited while checking invite, please try using a vpn !')
        
        finished = True
        logger.success('Finished joining job, press enter to get back to main menu !')
        input('')
        Utils.set_title({
            'Module': 'Main Menu'
        }, time())
        return
    elif context.status_code == 404:
        logger.error(f'Unknown invite')

        finished = True
        logger.success('Finished joining job, press enter to get back to main menu !')
        input('')
        Utils.set_title({
            'Module': 'Main Menu'
        }, time())
        return
    else:
        logger.error(f'Error while checking invite | {context.text}')

        finished = True
        logger.success('Finished joining job, press enter to get back to main menu !')
        input('')
        Utils.set_title({
            'Module': 'Main Menu'
        }, time())
        return

    while len(tokens) > 0:
        while len(thread_list) >= config['thread']:
            sleep(0.1)
            for thread in thread_list:
                if not thread.is_alive():
                    thread_list.remove(thread)
        
        token = tokens.pop(0)
        thread = Thread(target=joining_thread, args=[token, [invite, context], choice(proxies)])
        thread.start()
        thread_list.append(thread)
    for thread in thread_list:
        thread.join()
    
    finished = True
    logger.success('Finished joining job, press enter to get back to main menu !')
    input('')
    Utils.set_title({
        'Module': 'Main Menu'
    }, time())