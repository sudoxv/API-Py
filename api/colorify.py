import websockets
import json
import base64
import random
import string

class ColorifyAI:
    def __init__(self):
        self.base_url = "wss://colorifyai.art"
        self.session_hash = self._generate_hash()

    def _generate_hash(self):
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=12))

    async def _create_socket(self, endpoint, data):
        uri = f"{self.base_url}/{endpoint}/queue/join"
        async with websockets.connect(uri) as websocket:
            await websocket.send(json.dumps({ "session_hash": self.session_hash }))

            while True:
                message = await websocket.recv()
                d = json.loads(message)

                if d.get("msg") == "send_hash":
                    await websocket.send(json.dumps({ "session_hash": self.session_hash }))
                elif d.get("msg") == "send_data":
                    await websocket.send(json.dumps({ "session_hash": self.session_hash, "fn_index": 0, "data": data }))
                elif d.get("msg") == "process_completed":
                    return d["output"]["result"][0]
                elif d.get("msg") in ["estimation", "process_starts"]:
                    continue
                elif d.get("msg") == "queue_full":
                    raise Exception("Server queue is full.")
                else:
                    continue

    async def text2sketch(self, prompt, *, ratio='1:1', style='default'):
        valid_ratios = ['1:1', '3:4', '4:3', '9:16', '16:9', '2:3', '3:2']
        valid_styles = ['default', 'sci-fi', 'pixel', 'chibi', 'graffiti', 'minimalist', 'anime']

        if not prompt:
            raise ValueError("Prompt is required")
        if ratio not in valid_ratios:
            raise ValueError(f"Invalid ratio. Available: {', '.join(valid_ratios)}")
        if style not in valid_styles:
            raise ValueError(f"Invalid style. Available: {', '.join(valid_styles)}")

        data = {
            "aspect_ratio": ratio,
            "prompt": prompt,
            "request_from": 10,
            "style": style
        }
        return await self._create_socket("demo-colorify-text2img", data)

    async def image2sketch(self, buffer):
        if not buffer:
            raise ValueError("Image buffer is required")

        base64_image = f"data:image/jpeg;base64,{base64.b64encode(buffer).decode()}"
        data = {
            "source_image": base64_image,
            "request_from": 10
        }
        result = await self._create_socket("demo-colorify-img2img", data)
        return f"https://temp.colorifyai.art/{result}"
