from modules.discord import Discord
from modules.utils   import Utils
from threading       import Thread
from random          import choice
from time            import sleep, time

logger = Utils.get_logger()

tokens_file = Utils.get_file('input/tokens.txt')
ids_file = Utils.get_file('input/ids.txt')
proxies_file = Utils.get_file('input/proxies.txt')
config = Utils.get_config(True)

def itu_task():
    logger.clear()
    logger.print_banner('Starting converting job!')
    global finished, tokens, ids

    finished = False

    tokens = tokens_file.get_lines(True)
    proxies = proxies_file.get_lines(True)
    ids = ids_file.get_lines(True)

    def title_thread():
        global finished, tokens
        ids_len = len(ids)
        timestamp = time()
        while not finished:
            Utils.set_title({
                'Module': 'Id To User',
                'Total': f'{ids_len-len(ids)}/{ids_len}'
            }, timestamp)

    def itu_thread(unformatted_token:str, proxy:str=None):
        global ids
        token = Utils.get_token_from_str(unformatted_token)
        while True:
            try:
                discord = Discord(token, proxy)
                break
            except Exception as e:
                logger.error(f'{token[:-10]}********** {e}')
        discord.connect_to_ws()
        while len(ids) > 0:
            id = ids.pop(0)
            try:
                username = discord.get_user_from_id(id)
                logger.success(f'{token[:-10]}********** {username}')
                with open('input/users.txt', 'a') as f:
                    f.write(f'{username}\n')
            except Exception as e:
                logger.error(f'{token[:-10]}********** {e}')
                ids.append(id)
        
    thread_list = []
    Thread(target=title_thread).start()
    while len(tokens) > 0:
        while len(thread_list) >= config['thread']:
            sleep(0.1)
            for thread in thread_list:
                if not thread.is_alive():
                    thread_list.remove(thread)
        
        token = tokens.pop(0)
        thread = Thread(target=itu_thread, args=[token, choice(proxies)])
        thread.start()
        thread_list.append(thread)
    for thread in thread_list:
        thread.join()
    finished = True
    logger.success('Finished converting, press enter to get back to main menu !')
    input('')
    Utils.set_title({
        'Module': 'Main Menu'
    }, time())