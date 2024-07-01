from modules.utils import Utils
from websocket     import WebSocket
from datetime      import datetime
from random        import randint
from base64        import b64encode
from httpx         import get
from time          import mktime
from json          import loads, dumps
import re

html_content = get('https://discord.com/register').text
end_pos = html_content.find('" defer></script>')
if end_pos != -1:
    start_pos = html_content.rfind('<script src="', 0, end_pos)
    if start_pos != -1:
        script_tag = html_content[start_pos:end_pos + len('" defer></script>')]
        script = script_tag[len('<script src="'):-len('" defer></script>')]

js_content = get("https://discord.com" + script).text
build_number = re.search(r'buildNumber:"(\d{6})"', js_content).group(1)


xprops = {
   "os":"Windows",
   "browser":"Chrome",
   "device":"",
   "system_locale":"fr-FR",
   "browser_user_agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
   "browser_version":"124.0.0.0",
   "os_version":"10",
   "referrer":"",
   "referring_domain":"",
   "referrer_current":"",
   "referring_domain_current":"",
   "release_channel":"stable",
   "client_build_number":build_number,
   "client_event_source":None,
   "design_id":0
}
xsuperprops = b64encode(dumps(xprops).encode()).decode()

def nonce():
    date = datetime.now()
    unixts = mktime(date.timetuple())
    return str((int(unixts) * 1000 - 1420070400000) * 4194304)

class Discord:
    def __init__(self, token:str, proxies:str) -> None:
        self.token = token
        self.proxies = proxies

        self.session = Utils.get_tls_client(proxies)
        self.session.headers = {
            'authority': 'discord.com',
            'accept': '*/*',
            'accept-language': 'fr-FR,fr;q=0.8',
            'authorization': token,
            'content-type': 'application/json',
            'origin': 'https://discord.com',
            'sec-ch-ua': '"Brave";v="124", "Chromium";v="124", "Not?A_Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'sec-gpc': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            'x-debug-options': 'bugReporterEnabled',
            'x-discord-locale': 'fr',
            'x-discord-timezone': 'Europe/Paris',
            'x-super-properties': xsuperprops,
        }

    def connect_to_ws(self):
        self.ws = WebSocket()
        self.ws.connect('wss://gateway-us-east1-c.discord.gg/?encoding=json&v=9')
        self.ws.recv()
        self.ws.send('{"op":2,"d":{"token":"' + self.token + '","capabilities":16381,"properties":{"os":"Windows","browser":"Chrome","device":"","system_locale":"fr-FR","browser_user_agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36","browser_version":"124.0.0.0","os_version":"10","referrer":"","referring_domain":"","referrer_current":"","referring_domain_current":"","release_channel":"stable","client_build_number":247539,"client_event_source":null},"presence":{"status":"online","since":0,"activities":[],"afk":false},"compress":false,"client_state":{"guild_versions":{},"highest_last_message_id":"0","read_state_version":0,"user_guild_settings_version":-1,"user_settings_version":-1,"private_channels_version":"0","api_code_version":0}}}')
        
        res = loads(self.ws.recv())

        self.analytics_token = res["d"]["analytics_token"]
        self.session_id = res['d']['session_id']

        self.ws.send('{"op":4,"d":{"guild_id":null,"channel_id":null,"self_mute":true,"self_deaf":false,"self_video":false,"flags":2}}')

        self.send_science()

    def unflag(self):
        try:
            self.session.patch(
                'https://discord.com/api/v9/users/@me/agreements',
                json={
                    'terms': True,
                    'privacy': True,
                }
            )
            return True
        except Exception as e:
            return str(e)

    def send_science(self):
        #https://github.com/Merubokkusu/Discord-S.C.U.M/blob/master/discum/science/science.py
        now = int(mktime(datetime.now().timetuple()) * 1000)
        self.session.post(
            'https://discord.com/api/v9/science',
            json={
                'token': self.analytics_token,
                'events': [
                    {
                        'type': 'friends_list_viewed',
                        'properties': {
                            'client_track_timestamp': now,
                            'client_heartbeat_session_id': 'ddae518c-3ffe-4359-87ac-cd050981e7db',
                            'tab_opened': 'ADD_FRIEND',
                            'client_performance_memory': 0,
                            'accessibility_features': 524544,
                            'rendered_locale': 'fr',
                            'uptime_app': 33382,
                            'client_rtc_state': 'DISCONNECTED',
                            'client_app_state': 'focused',
                            'client_uuid': 'HiAEMSEVSRDtXx8hrLCgz4sBAABhAAAA',
                            'client_send_timestamp': now+randint(40, 1000),
                        },
                    },
                ],
            }
        )

    def get_user_from_id(self, id:str):
        response = self.session.get(
            f'https://discord.com/api/users/{id}'
        ).json()
        if response["discriminator"] == "0":
            return f'{response["username"]}#null'
        else:
            return f'{response["username"]}#{response["discriminator"]}'

    def add_relationship(self, username:str, discriminator:int=None):
        response = self.session.post(
            'https://discord.com/api/v9/users/@me/relationships',
            json={
                'username': username,
                'discriminator': discriminator,
            }
        )
        if response.status_code == 204:
            return True
        elif 'captcha' in response.text:
            return 'captcha'
        elif '40002' in response.text:
            return 'locked'
        else:
            return response.text
    
    def join_server(self, invite:str, context:str, rqtoken:str=None,captcha_key:str=None, tries:int=0) -> str:
        if tries == 3:
            return 'captcha_failed'
        # ik shit code but when me using this no cap so i use this ok ?
        headers = {
            'Accept': '*/*',
            'Accept-Language': 'fr-FR,fr;q=0.9',
            'Authorization': self.token,
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json',
            'Origin': 'https://discord.com',
            'Pragma': 'no-cache',
            'Referer': 'https://discord.com/channels/@me',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-GPC': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
            'X-Debug-Options': 'bugReporterEnabled',
            'X-Discord-Locale': 'fr',
            'X-Discord-Timezone': 'Europe/Paris',
            'X-Super-Properties': xsuperprops,
            'sec-ch-ua': '"Chromium";v="118", "Brave";v="118", "Not=A?Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }
        headers['x-context-properties'] = context
        if rqtoken != None:
            headers.update({
                "x-captcha-rqtoken": rqtoken,
                "x-captcha-key": captcha_key[1]
            })
        response = self.session.post(
            f'https://discord.com/api/v9/invites/{invite}',
            headers=headers,
            json={
                'session_id': self.session_id
            }
        )
        if response.status_code == 200:
            return True
        elif response.status_code == 429:
            try:
                return f'rate_limited_{round(response.json()["retry_after"])+1}'
            except:
                return "cloudflare_rate_limite"
        elif response.status_code == 404:
            return 'invalid'
        elif response.status_code == 403:
            print(response.text)
            return 'locked'
        elif response.status_code == 400:
            if 'captcha_rqtoken' not in response.json():
                return 'locked'
            return f'captcha_solve_{response.json()["captcha_rqtoken"]}_{response.json()["captcha_rqdata"]}'
        else:
            return response.text
    
    def change_at_me(self, payload:dict=None):
        response = self.session.patch(
            'https://discord.com/api/v9/users/@me',
            json=payload
        )
        match response.status_code:
            case 200:
                return True
            case 401:
                return "locked"
            case 403:
                return "locked"
            case 400:
                return "captcha"
            case _:
                return response.text
    
    def change_profile(self, payload:dict=None):
        response = self.session.patch(
            'https://discord.com/api/v9/users/%40me/profile',
            json=payload
        )
        match response.status_code:
            case 200:
                return True
            case 401:
                return "locked"
            case 403:
                return "locked"
            case 400:
                return "captcha"
            case _:
                return response.text
    
    def open_channel(self, id:str) -> str:
        response = self.session.post(
                'https://discord.com/api/v9/users/@me/channels',
                json={
                    'recipients': [ id ]
                }
        )
        match response.status_code:
            case 200:
                return [True, response.json()['id']]
            case 401:
                return "locked"
            case 403:
                return "locked"
            case 429:
                return "sleep"
            case _:
                return [False, response.text]
        
    def send_message(self, content:str, c_id:str, captchaDict:dict=None):
        headers = self.session.headers.copy()

        if captchaDict != None:
            headers['X-Captcha-Rqtoken'] = captchaDict['X-Captcha-Rqtoken']
            headers['X-Captcha-Key'] = captchaDict['X-Captcha-Key']

        response = self.session.post(
            f'https://discord.com/api/v9/channels/{c_id}/messages',
            headers=headers,
            json={
                'content': content,
                'nonce': nonce(),
                'tts': False,
                'flags': 0
            }
        )

        match response.status_code:
            case 200:
                return True
            case 401:
                return "locked"
            case 403:
                return "locked"
            case 400:
                return f'captcha_solve_{response.json()["captcha_rqtoken"]}_{response.json()["captcha_rqdata"]}'
            case 429:
                return "sleep"
            case _:
                return response.text
