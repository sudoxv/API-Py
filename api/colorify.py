import asyncio
import websockets
import json
import base64
import random
import string

class ColorifyAI:
    def __init__(self):
        self.base_url = "wss://colorifyai.art"

    def _generate_hash(self):
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=12))

    async def _create_socket(self, endpoint, data):
        session_hash = self._generate_hash()
        uri = f"{self.base_url}/{endpoint}/queue/join"

        async with websockets.connect(uri) as websocket:
            await websocket.send(json.dumps({ "session_hash": session_hash }))

            while True:
                raw_msg = await websocket.recv()
                msg = json.loads(raw_msg)

                if msg.get("msg") == "send_hash":
                    await websocket.send(json.dumps({ "session_hash": session_hash }))
                elif msg.get("msg") == "send_data":
                    await websocket.send(json.dumps({
                        "session_hash": session_hash,
                        "fn_index": 0,
                        "data": data
                    }))
                elif msg.get("msg") == "process_completed":
                    result = msg["output"]["result"][0]
                    return result
                elif msg.get("msg") in ["estimation", "process_starts"]:
                    continue
                elif msg.get("msg") == "queue_full":
                    raise Exception("Queue penuh di server ColorifyAI")
                else:
                    continue

    async def text2sketch(self, prompt, ratio='1:1', style='default'):
        valid_ratios = ['1:1', '3:4', '4:3', '9:16', '16:9', '2:3', '3:2']
        valid_styles = ['default', 'sci-fi', 'pixel', 'chibi', 'graffiti', 'minimalist', 'anime']

        if not prompt:
            raise ValueError("Prompt diperlukan")
        if ratio not in valid_ratios:
            raise ValueError(f"Ratio harus salah satu dari: {', '.join(valid_ratios)}")
        if style not in valid_styles:
            raise ValueError(f"Style harus salah satu dari: {', '.join(valid_styles)}")

        data = {
            "aspect_ratio": ratio,
            "prompt": prompt,
            "request_from": 10,
            "style": style
        }

        return await self._create_socket("demo-colorify-text2img", data)

    async def image2sketch(self, image_bytes):
        if not image_bytes:
            raise ValueError("Gambar harus diberikan dalam bentuk bytes")

        base64_image = base64.b64encode(image_bytes).decode()
        data = {
            "request_from": 10,
            "source_image": f"data:image/jpeg;base64,{base64_image}"
        }

        result = await self._create_socket("demo-colorify-img2img", data)
        return f"https://temp.colorifyai.art/{result}"
