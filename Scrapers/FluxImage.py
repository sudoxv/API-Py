import requests
import json
import random
import sseclient

class Flux:
    def __init__(self, prompt):
        self.base_url = "https://black-forest-labs-flux-1-schnell.hf.space"
        self.prompt = prompt

    def generate_session_hash(self):
        return ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=10))

    def request(self):
        session_hash = self.generate_session_hash()
        data = json.dumps({
            "data": [self.prompt, 0, True, 1024, 1024, 4],
            "event_data": None,
            "fn_index": 2,
            "trigger_id": 5,
            "session_hash": session_hash
        })
        headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
            'Content-Type': 'application/json',
            'sec-ch-ua-platform': '"Android"',
            'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
            'dnt': '1',
            'sec-ch-ua-mobile': '?1',
            'origin': self.base_url,
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': self.base_url + '/',
            'accept-language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7',
            'priority': 'u=1, i'
        }
        response = requests.post(self.base_url + "/queue/join", headers=headers, data=data)
        return {"event": response.json()["event_id"], "session_hash": session_hash}

    def check_status(self, session_hash):
        url = f"{self.base_url}/queue/data?session_hash={session_hash}"
        response = sseclient.SSEClient(url)
        for event in response:
            print(event)
            data = json.loads(event.data)
            if data["msg"] == "process_completed":
                return data
            elif data["msg"] == "error":
                raise Exception(data)
            else:
                print("Event:", data)

    def generate(self):
        try:
            req = self.request()
            check = self.check_status(req["session_hash"])
            return { "url": check["output"]["data"][0]["url"] }
        except Exception as e:
            print("Error:", e)
