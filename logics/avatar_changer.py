from modules.discord import Discord
from modules.utils   import Utils
from threading       import Thread
from random          import choice
from base64          import b64encode
from time            import sleep, time
from os              import listdir, path

logger = Utils.get_logger()

tokens_file = Utils.get_file('input/tokens.txt')
proxies_file = Utils.get_file('input/proxies.txt')
config = Utils.get_config(True)

# Thx Gpt for this W script
avatar_b64 = []
for file in listdir('input/avatars'):
    if file.endswith(".png") or file.endswith(".jpg"):
        file_path = path.join('input/avatars', file)

        with open(file_path, "rb") as f:
            content = f.read()

        encoded = b64encode(content).decode("utf-8")

        formatted_type = "image/png" if file.endswith(".png") else "image/jpeg"
        formatted_data = f"data:{formatted_type};base64,{encoded}"

        avatar_b64.append(formatted_data)

def avatar_task():
    logger.clear()
    logger.print_banner('Starting avatar changing job!')
    global sucesss, failed
    global finished, tokens

    sucesss, failed = 0, 0
    finished = False

    tokens = tokens_file.get_lines(True)
    proxies = proxies_file.get_lines(True)

    def title_thread():
        global sucesss, failed
        global finished, tokens
        tokens_len = len(tokens)
        timestamp = time()
        while not finished:
            Utils.set_title({
                'Module': 'Avatar Changer',
                'Accepted': sucesss,
                'Failed': failed,
                'Total': f'{tokens_len-len(tokens)}/{tokens_len}',
                'Token Left': len(tokens)
            }, timestamp)

    def avatar_thread(unformatted_token:str, avatar:str, proxy:str=None):
        global sucesss, failed
        token = Utils.get_token_from_str(unformatted_token)
        while True:
            try:
                discord = Discord(token, proxy)
                break
            except Exception as e:
                logger.error(f'{token[:-10]}********** {e}')
        discord.connect_to_ws()
        accepted = discord.change_at_me({'avatar': avatar})
        while accepted not in [True, 'locked', 'captcha']:
            logger.error(f'{token[:-10]}********** {accepted}')
            accepted = discord.change_at_me({'avatar': avatar})
        match accepted:
            case True:
                logger.success(f'{token[:-10]}********** Changed avatar')
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
        thread = Thread(target=avatar_thread, args=[token, choice(avatar_b64), choice(proxies)])
        thread.start()
        thread_list.append(thread)
    for thread in thread_list:
        thread.join()
    finished = True
    logger.success('Finished avatar changing job, press enter to get back to main menu !')
    input('')
    Utils.set_title({
        'Module': 'Main Menu'
    }, time())