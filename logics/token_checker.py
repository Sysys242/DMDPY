from modules.utils import Utils
from threading     import Thread
from random        import choice
from time          import time, sleep

logger = Utils.get_logger()
tokens_file = Utils.get_file('input/tokens.txt')
proxies_file = Utils.get_file('input/proxies.txt')

def checking_task():
    global tokens, proxies, session, finished
    global valid, unverified, invalid, _valid, _unverified, _invalid

    valid, unverified, invalid = [], [], []
    _valid, _unverified, _invalid = 0, 0, 0
    finished = False

    config = Utils.get_config(True)

    tokens = tokens_file.get_lines(True)
    proxies = proxies_file.get_lines(True)

    session = Utils.get_tls_client('')

    def title_thread():
        global sucesss, failed
        global finished, tokens, _valid, _unverified, _invalid
        tokens_len = len(tokens)
        timestamp = time()
        while not finished:
            Utils.set_title({
                'Module': 'Token Checker',
                'Valid': _valid,
                'Unverified': _unverified,
                'Invalid': _invalid,
                'Total': f'{tokens_len-len(tokens)}/{tokens_len}',
                'Token Left': len(tokens)
            }, timestamp)
            sleep(0.5)

    def writting_thread():
        global valid, unverified, invalid, finished
        while not finished:
            with open('input/checker/invalids.txt', 'a') as f:
                while len(invalid) > 0:
                    token = invalid.pop(0)
                    f.write(f'{token}\n')
            
            with open('input/checker/unverified.txt', 'a') as f:
                while len(unverified) > 0:
                    token = unverified.pop(0)
                    f.write(f'{token}\n')
            
            with open('input/checker/valids.txt', 'a') as f:
                while len(valid) > 0:
                    token = valid.pop(0)
                    f.write(f'{token}\n')
            sleep(0.5)
        
        with open('input/checker/invalids.txt', 'a') as f:
            while len(invalid) > 0:
                token = invalid.pop(0)
                f.write(f'{token}\n')
            
        with open('input/checker/unverified.txt', 'a') as f:
            while len(unverified) > 0:
                token = unverified.pop(0)
                f.write(f'{token}\n')
            
        with open('input/checker/valids.txt', 'a') as f:
            while len(valid) > 0:
                token = valid.pop(0)
                f.write(f'{token}\n')

    def checking_thread():
        global tokens, proxies, session
        global valid, unverified, invalid, _valid, _unverified, _invalid

        while len(tokens) > 0:
            token = tokens.pop(0)
            _token = Utils.get_token_from_str(token)

            try:
                response = session.get(
                    'https://discord.com/api/v9/users/@me/burst-credits',
                    headers={
                        'Authorization': _token
                    },
                    proxy={
                        "http": f"http://{choice(proxies)}",
                        "https": f"http://{choice(proxies)}"
                    }
                )
                match response.status_code:
                    case 200:
                        valid.append(token); _valid += 1
                        logger.success(f'{_token} Valid')
                    case 401:
                        invalid.append(token); _invalid += 1
                        logger.error(f'{_token} Invalid')
                    case 403:
                        unverified.append(token); _unverified += 1
                        logger.error(f'{_token} Locked')
                    case 429:
                        with open('input/checker/errors.txt', 'a') as f:
                            f.write(f'{token}\n')
                        logger.error(f'{_token} Rate limited')
                    case _:
                        with open('input/checker/errors.txt', 'a') as f:
                            f.write(f'{token}\n')
                        logger.error(f'{_token} {response.text} | {response.status_code}')
            except Exception as e:
                logger.error(f'{_token} {e}')
                with open('input/checker/errors.txt', 'a') as f:
                    f.write(f'{token}\n')
    
    thread_list = []
    Thread(target=title_thread).start()
    Thread(target=writting_thread).start()
    while len(tokens) > 0:
        while len(thread_list) >= config['token-checker']['thread']:
            sleep(0.1)
            for thread in thread_list:
                if not thread.is_alive():
                    thread_list.remove(thread)
        
        thread = Thread(target=checking_thread)
        thread.start()
        thread_list.append(thread)
    for thread in thread_list:
        thread.join()
    finished = True
    logger.success('Finished checking job, look at input/checker, press enter to get back to main menu !')
    input('')
    Utils.set_title({
        'Module': 'Main Menu'
    }, time())