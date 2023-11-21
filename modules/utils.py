from modules.logger  import Logger
from modules.file    import File
from tls_client      import Session
from datetime        import timedelta
from ctypes          import windll
from yaml            import safe_load
from time            import time
from re              import search
        
    
config = File('input/config.yml')
logger = Logger()

class Utils:
    def get_version() -> str:
        return '1.0.0'

    def get_tls_client(proxy:str) -> Session:
        session = Session(
            client_identifier="chrome_118",
            random_tls_extension_order=True
        )
        if proxy != '':
            session.proxies = 'http://' + proxy

        session.get('https://discord.com/')
        session.cookies.set('locale', 'fr')

        return session
    
    def get_config(reload=True):
        return safe_load(config.get_content(reload))
    
    def get_logger() -> Logger:
        return logger
    
    def set_title(infos:dict, timestamp):
        title = f'DMDPY {Utils.get_version()}'
        for info in infos:
            title += f" | {info}: {infos[info]}"
        
        delta = timedelta(seconds=round(time()-timestamp))
        result = ""
        if delta.days > 0:
            result += f"{delta.days}d "
        if delta.seconds // 3600 > 0:
            result += f"{delta.seconds // 3600}h "
        if delta.seconds // 60 % 60 > 0:
            result += f"{delta.seconds // 60 % 60}m "
        if delta.seconds % 60 > 0 or result == "":
            result += f"{delta.seconds % 60}s"
        windll.kernel32.SetConsoleTitleW(title)
    
    def get_file(path:str) -> File:
        return File(path)
    
    def save(text:str, file:str, remove_from_token:bool=False, output=True):
        if output:
            with open(f'output/{file}.txt', 'a') as f:
                f.write(f'{text}\n')
        else:
            with open(f'input/{file}.txt', 'a') as f:
                f.write(f'{text}\n')
        
        if remove_from_token:
            if ':' in text:
                token = text.split(':')[2]
            else:
                token = text
            
            with open('input/tokens.txt', 'r') as f:
                lines = f.readlines()

            for line in lines:
                if token in line:
                    lines.remove(line)

            with open('input/tokens.txt', 'w') as f:
                f.writelines(lines)

    def get_val_from_index(dictionary:dict, n=0):
        """https://stackoverflow.com/questions/4326658/how-to-index-into-a-dictionary"""
        if n < 0:
            n += len(dictionary)
        for i, values in enumerate(dictionary.values()):
            if i == n:
                return values
        return False

    def get_token_from_str(token: str) -> str:
        pattern = r"[\w-]{24,26}\.[\w-]{6}\.[\w-]{38}"
        if ":" in token:
            match = search(pattern, token)
            if match:
                return match.group(0)
        return token