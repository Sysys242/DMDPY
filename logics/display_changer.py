from modules.discord import Discord
from modules.utils   import Utils
from threading       import Thread
from random          import choice
from time            import sleep, time

logger = Utils.get_logger()

tokens_file = Utils.get_file('input/tokens.txt')
proxies_file = Utils.get_file('input/proxies.txt')
names_file = Utils.get_file('input/display_names.txt')
config = Utils.get_config(True)


def display_task():
    logger.clear()
    logger.print_banner('Starting display changing job!')
    global sucesss, failed
    global finished, tokens

    sucesss, failed = 0, 0
    finished = False

    tokens = tokens_file.get_lines(True)
    proxies = proxies_file.get_lines(True)
    names = names_file.get_lines(True)

    def title_thread():
        global sucesss, failed
        global finished, tokens
        tokens_len = len(tokens)
        timestamp = time()
        while not finished:
            Utils.set_title({
                'Module': 'Display Name Changer',
                'Accepted': sucesss,
                'Failed': failed,
                'Total': f'{tokens_len-len(tokens)}/{tokens_len}',
                'Token Left': len(tokens)
            }, timestamp)

    def display_thread(unformatted_token:str, name:str, proxy:str=None):
        global sucesss, failed
        token = Utils.get_token_from_str(unformatted_token)
        while True:
            try:
                discord = Discord(token, proxy)
                break
            except Exception as e:
                logger.error(f'{token[:-10]}********** {e}')
        discord.connect_to_ws()
        accepted = discord.change_at_me({'global_name': name})
        while accepted not in [True, 'locked', 'captcha']:
            logger.error(f'{token[:-10]}********** {accepted}')
            accepted = discord.change_at_me({'global_name': name})
        match accepted:
            case True:
                logger.success(f'{token[:-10]}********** Changed display name')
            case "captcha":
                logger.error(f'{token[:-10]}********** Captcha Detected')
            case "locked":
                logger.error(f'{token[:-10]}********** Token Locked')
            case _:
                logger.error(f'{token[:-10]}********** {accepted}')


        
    thread_list = []
    Thread(target=title_thread).start()
    while len(tokens) > 0:
        while len(thread_list) >= config['thread']:
            sleep(0.1)
            for thread in thread_list:
                if not thread.is_alive():
                    thread_list.remove(thread)
        
        token = tokens.pop(0)
        thread = Thread(target=display_thread, args=[token, choice(names), choice(proxies)])
        thread.start()
        thread_list.append(thread)
    for thread in thread_list:
        thread.join()
    finished = True
    logger.success('Finished display changing job, press enter to get back to main menu !')
    input('')
    Utils.set_title({
        'Module': 'Main Menu'
    }, time())