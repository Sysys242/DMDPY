from urllib.parse import urlparse
from tls_client   import Session
from time         import sleep

class Hcoptcha:
    def __init__(self, api_key:str) -> None:
        self.key = api_key
        self.session = Session(
            client_identifier="chrome_118",
            random_tls_extension_order=True
        )

    def create_task(self, proxy:str, site_key:str, rqdata:str=None) -> list:
        payload = {
            "api_key": self.key,
            'task_type': 'hcaptchaEnterprise',
            "data": {
                "url": "https://discord.com/",
                "sitekey": site_key,
                "proxy": proxy.replace('http://', ''),
                "useragent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
            }
        }
        if rqdata is not None:
            payload['data']['rqdata'] = rqdata

        response = self.session.post(
            'https://api.hcoptcha.online/api/createTask',
            json=payload
        )
        if response.json()['error'] is False:
            return [True, response.json()['task_id']]
        else:
            return [False, response.json()['error']]
    
    def get_task_solution(self, task_id:str) -> list:
        response = self.session.post(
            'https://api.hcoptcha.online/api/getTaskData',
            json={
                "api_key": self.key,
                "task_id": task_id
            }
        )
        if response.json()['task']['state'] == 'completed':
            return ['ready', response.json()['task']['captcha_key']]
        else:
            if "errorDescription" in response.json():
                return [response.json()['task']['state'], response.json()['errorDescription']]
            else:
                return [response.json()['task']['state'], "errorw"]
        
    def solve_captcha(self, proxy:str, site_key:str, rqdata:str=None) -> str:
        task_id = self.create_task(proxy, site_key, rqdata)
        if not task_id[0]:
            return 'error'
        
        solution = self.get_task_solution(task_id[1])
        while solution[0] not in ['ready', 'error']:
            sleep(0.5)
            solution = self.get_task_solution(task_id[1])
        if solution[0] == 'ready':
            return solution
        return 'error'

class Capmonster:
    def __init__(self, api_key:str) -> None:
        self.key = api_key
        self.session = Session(
            client_identifier="chrome_118",
            random_tls_extension_order=True
        )
    def create_task(self, proxy:str, site_key:str, rqdata:str=None) -> list:
        parsed = urlparse(proxy)
    
        proxy_dict = {
            "proxyType": "http",
            "proxyAddress": parsed.hostname,
            "proxyPort": parsed.port,
        }
        
        if parsed.username and parsed.password:
            proxy_dict["proxyLogin"] = parsed.username
            proxy_dict["proxyPassword"] = parsed.password
        
        payload = {
            "clientKey": self.key,
            "task": {
                "type": "HCaptchaTask",
                "websiteURL": "https://discord.com/",
                "websiteKey": site_key,
                "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
                **proxy_dict
            }
        }

        if rqdata is not None:
            payload['task']['data'] = rqdata

        response = self.session.post(
            'https://api.capmonster.cloud/createTask',
            json=payload
        )
        if response.json()['errorId'] == 0:
            return [True, response.json()['taskId']]
        else:
            return [False, response.json()['errorCode']]
    
    def get_task_solution(self, task_id:str) -> list:
        response = self.session.post(
            'https://api.capmonster.cloud/getTaskResult',
            json={
                "clientKey": self.key,
                "taskId": task_id
            }
        )
        if response.json()['status'] == 'ready':
            return ['ready', response.json()['solution']['gRecaptchaResponse']]
        else:
            return [response.json()['status'], response.json()['errorDescription']]
        
    def solve_captcha(self, proxy:str, site_key:str, rqdata:str=None) -> str:
        task_id = self.create_task(proxy, site_key, rqdata)
        if not task_id[0]:
            return 'error'
        
        solution = self.get_task_solution(task_id[1])
        while solution[0] == 'processing':
            sleep(0.5)
            solution = self.get_task_solution(task_id[1])
        if solution[0] == 'ready':
            return solution[1]
        return 'error'

class Null:
    def solve_captcha(self, _, __,___):
        return 'not_solving'

class Solver:
    def __init__(self, api_key:str, api_type:str) -> None:
        self.key = api_key
        if api_type == 'capmonster':
            self.api = Capmonster(
                self.key
            )
        elif api_type == "hcoptcha":
            self.api = Hcoptcha(
                self.key
            )
        else:
            self.api = Null()
    
    def solve(self, proxy:str, site_key:str, rqdata=None):
        return self.api.solve_captcha(proxy, site_key, rqdata)