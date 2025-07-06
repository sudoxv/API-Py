import requests
import json
import random
import sseclient

class Qwen:
    def __init__(self, prompt, system="Kamu adalah Asisten AI yang pintar", session_hash=None):
        self.base_url = "https://qwen-qwen3-demo.hf.space"
        self.prompt = prompt
        self.system = system
        self.session_hash = session_hash

    def generate_session_hash(self):
        return ''.join(random.choices('abcdefghijklmnopqrstuvxyz0123456789', k=10))

    def request(self):
        session_hash = self.session_hash if self.session_hash is not None else self.generate_session_hash()
        data = json.dumps({
            "data": [self.prompt, {
                "model": "qwen3-235b-a22b",
                "sys_prompt": self.system,
                "thinking_budget": 38
            }, None, None],
            "event_data": None,
            "fn_index": 13,
            "trigger_id": 31,
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
        response = requests.post(self.base_url + "/gradio_api/queue/join", headers=headers, data=data)
        return {
            "event": response.json()["event_id"],
            "session_hash": session_hash
        }

    def check_status(self, session_hash):
        url = f"{self.base_url}/gradio_api/queue/data?session_hash={session_hash}"
        response = sseclient.SSEClient(url)
        for event in response:
            try:
                data = json.loads(event.data)
                if data["msg"] == "process_completed":
                    return data
                elif data["msg"] == "error":
                    raise Exception(data)
                else:
                    print("Event:", data)
            except json.JSONDecodeError:
                print("Invalid JSON:", event.data)

    def generate(self):
        try:
            req = self.request()
            session_hash = req["session_hash"]
            check = self.check_status(session_hash)
            return { "data": check["output"]["data"][len(check["output"]["data"]) - 2]["value"], "session_hash": session_hash }
        except Exception as e:
            print("Error:", e)
