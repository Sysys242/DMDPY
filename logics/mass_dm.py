from modules.discord    import Discord
from modules.solver     import Solver
from modules.utils      import Utils
from threading          import Thread
from random             import choice
from time               import sleep, time

tokens_file = Utils.get_file('input/tokens.txt')
proxies_file = Utils.get_file('input/proxies.txt')
ids_file = Utils.get_file('input/ids.txt')

logger = Utils.get_logger()

def dming_task():
    logger.clear()
    logger.print_banner('Starting friending job!')
    global ids, unlocked, locked, sent, failed, captcha, solver, finished
    global tokens, used

    tokens = tokens_file.get_lines(True)
    proxies = proxies_file.get_lines(True)
    ids = ids_file.get_lines(True)

    config = Utils.get_config(True)

    solver = Solver(
        config['captcha']['key'],
        config['captcha']['service'],
    )

    unlocked, locked, sent, failed, captcha, used = len(tokens), 0, 0, 0, 0, 0
    finished = False

    config = Utils.get_config()

    def title_thread():
        global sent, failed, captcha, ids, used
        global finished, tokens, unlocked, locked
        ids_len = len(ids)
        timestamp = time()
        while not finished:
            if used != 0:
                average = f'{sent/used}'
            else:
                average = "None"
            Utils.set_title({
                'Module': 'MassDm',
                'Sent': sent,
                'Captcha': captcha,
                'Failed': failed,

                'Unlocked': unlocked,
                'Locked': locked,

                'Average': average,
                'Total': f'{ids_len-len(ids)}/{ids_len}',
                'Token Left': len(ids)
            }, timestamp)

    def dming_thread(unformatted_token:str, proxy:str):
        global used, sent, locked, unlocked, ids, failed, captcha
        _finished = False
        _sent = 0

        token = Utils.get_token_from_str(unformatted_token)
        while True:
            try:
                discord = Discord(token, proxy)
                break
            except Exception as e:
                logger.error(f'{token[:-10]}********** {e}')
        discord.connect_to_ws()
        used  += 1
        
        while len(ids) > 0 and not _finished:
            id = ''
            while id == '':
                id = ids.pop(0)

            channel_id = discord.open_channel(id)
            match channel_id:
                case "locked":
                    logger.error(f'{token[:-10]}********** Locked, stopping thread...')
                    ids.append(id)
                    _finished = True
                case "sleep":
                    logger.info(f'{token[:-10]}********** Rate limited, sleeping {config["mass-dm"]["rate-limit-time"]}')
                    ids.append(id)
                    sleep(config["mass-dm"]["rate-limit-time"])
                case _:
                    if channel_id[0] == False:
                        logger.error(f'{token[:-10]}********** Failed to open channel ({id}): {channel_id[1]}')
                        ids.append(id)
                    else:
                        captcha_dict = None
                        success = False
                        while not success:
                            message_response = discord.send_message(
                                config['mass-dm']['content'],
                                channel_id[1],
                                captcha_dict
                            )
                            match message_response:
                                case True:
                                    logger.success(f'{token[:-10]}********** Successfully sent message to {id} | {_sent}')
                                    _sent += 1
                                    sent += 1
                                    success = True
                                    sleep(config['mass-dm']['sleep-time'])
                                case "locked":
                                    logger.error(f'{token[:-10]}********** Locked, stopping thread...')
                                    ids.append(id)
                                    _finished = True
                                    locked += 1
                                    unlocked -= 1
                                    success = True
                                case "sleep":
                                    logger.info(f'{token[:-10]}********** Rate limited, sleeping {config["mass-dm"]["rate-limit-time"]}')
                                    sleep(config["mass-dm"]["rate-limit-time"])
                                case _:
                                    if 'captcha' in message_response:
                                        captcha += 1
                                        _captcha_key = solver.solve(proxy, 'e2f713c5-b5ce-41d0-b65f-29823df542cf', message_response.split('_')[3])
                                        if _captcha_key != 'not_solving':
                                            if _captcha_key == "error":
                                                logger.error(f'{token[:-10]}********** Failed to solve captcha!')
                                            else:
                                                captcha_dict = {
                                                    "X-Captcha-Rqtoken": message_response.split('_')[2],
                                                    "X-Captcha-Key": _captcha_key
                                                }
                                                logger.info(f'{token[:-10]}********** Solved captcha!')
                                    else:
                                        logger.error(f'{token[:-10]}********** Unknown error: {message_response}')
                                        failed += 1
                                        success = True
    
    thread_list = []
    Thread(target=title_thread).start()

    while len(tokens) > 0:
        while len(thread_list) >= config['thread']:
            sleep(0.1)
            for thread in thread_list:
                if not thread.is_alive():
                    thread_list.remove(thread)
        
        token = tokens.pop(0)
        thread = Thread(target=dming_thread, args=[token, choice(proxies)])
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