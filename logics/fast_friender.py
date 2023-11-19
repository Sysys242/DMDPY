from modules.discord import Discord
from modules.utils   import Utils
from threading       import Thread
from random          import choice
from time            import sleep, time

logger = Utils.get_logger()

users_file = Utils.get_file('input/users.txt')
tokens_file = Utils.get_file('input/tokens.txt')
proxies_file = Utils.get_file('input/proxies.txt')
config = Utils.get_config(True)

def fast_friending_task():
    logger.clear()
    logger.print_banner('Starting friending job!')
    global sucesss, failed, captcha
    global users, finished, tokens

    sucesss, failed, captcha = 0, 0, 0
    finished = False

    users = users_file.get_lines(True)
    tokens = tokens_file.get_lines(True)
    proxies = proxies_file.get_lines(True)

    def title_thread():
        global sucesss, failed, captcha
        global users, finished, tokens
        user_len = len(users)
        timestamp = time()
        while not finished:
            Utils.set_title({
                'Module': 'Fast Friender',
                'Sent': sucesss,
                'Captcha': captcha,
                'Failed': failed,
                'Total': f'{user_len-len(users)}/{user_len}',
                'Token Left': len(tokens)
            }, timestamp)

    def friending_thread(unformatted_token:str, proxy:str=None):
        global sucesss, failed, captcha
        global users, added
        added = 0

        token = Utils.get_token_from_str(unformatted_token)
        while True:
            try:
                discord = Discord(token, proxy)
                break
            except Exception as e:
                logger.error(f'{token[:-10]}********** {e}')
        discord.connect_to_ws()
        
        _thread_list = []
        for _ in range(config['friender']['number']):
            user = users.pop(0)
            while "#" not in user:
                user = users.pop(0)

            username, discrim = user.split('#')
            if discrim == "null":
                discrim = None

            def send(username, discrim):
                global sucesss, failed, captcha
                global users, added
                res = discord.add_relationship(username, discrim)
                match res:
                    case True:
                        added += 1
                        sucesss += 1
                        logger.success(f'{token[:-10]}********** Added {user} | {added}')
                    case 'captcha':
                        captcha += 1
                        logger.error(f'{token[:-10]}********** Failed to add {user} | {res} | {added}')
                    case _:
                        failed += 1
                        logger.error(f'{token[:-10]}********** Failed to add {user} | {res} | {added}')

            _thread = Thread(target=send, args=[username, discrim])
            _thread.start()
            _thread_list.append(_thread)
        for _thread in _thread_list:
            _thread.join()
            
        logger.info(f'{token[:-10]}********** Sent {added} friends requests | {added}')
        
    thread_list = []
    Thread(target=title_thread).start()
    while len(tokens) > 0 and len(users) > 0:
        while len(thread_list) >= config['thread']:
            sleep(0.1)
            for thread in thread_list:
                if not thread.is_alive():
                    thread_list.remove(thread)
        
        token = tokens.pop(0)
        thread = Thread(target=friending_thread, args=[token, choice(proxies)])
        thread.start()
        thread_list.append(thread)
    for thread in thread_list:
        thread.join()
    finished = True
    logger.success('Finished fast friending job, press enter to get back to main menu !')
    input('')
    Utils.set_title({
        'Module': 'Main Menu'
    }, time())