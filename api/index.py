from flask import Flask, jsonify, request
import asyncio
from .otakudesu import Otakudesu
from .cekresi import Cekresi
from .colorify import ColorifyAI

app = Flask(__name__)

@app.route("/")
def index():
    return "Hello, World!"

@app.route("/api/otakudesu/sedang-tayang", methods=["GET"])
def otakudesu_route():
    data = Otakudesu()
    return jsonify({ "status": 200, "result": data }), 200

@app.route("/api/cekresi", methods=["GET"])
def cekresi_route():
    try:
        nomer_resi = request.args.get("nomer_resi")
        ekspedisi = request.args.get("ekspedisi")
        if not nomer_resi:
            return jsonify({ "status": 400, "msg": 'Parameter "nomer_resi" tidak ditemukan' }), 400
        if not ekspedisi:
            return jsonify({ "status": 400, "msg": 'Parameter "ekspedisi" tidak ditemukan' }), 400

        result = Cekresi(nomer_resi, ekspedisi)
        return jsonify({ "status": 200, "result": result }), 200

    except ValueError as e:
        return jsonify({ "status": 400, "msg": str(e) }), 400
    except Exception as e:
        return jsonify({ "status": 500, "msg": f"Terjadi kesalahan: {str(e)}" }), 500

@app.route("/api/colorify/text2sketch", methods=["GET"])
def colorify_text2sketch():
    prompt = request.args.get("prompt")
    ratio = request.args.get("ratio", "1:1")
    style = request.args.get("style", "default")

    if not prompt:
        return jsonify({"status": 400, "msg": "Parameter 'prompt' wajib diisi."}), 400

    async def generate():
        try:
            colorify = ColorifyAI()
            result = await colorify.text2sketch(prompt, ratio=ratio, style=style)
            return jsonify({"status": 200, "result": result})
        except ValueError as e:
            return jsonify({"status": 400, "msg": str(e)}), 400
        except Exception as e:
            return jsonify({"status": 500, "msg": f"Terjadi kesalahan: {str(e)}"}), 500

    return asyncio.run(generate())

@app.route("/api/colorify/image2sketch", methods=["POST"])
def colorify_image2sketch():
    if "image" not in request.files:
        return jsonify({"status": 400, "msg": "Form-data 'image' tidak ditemukan"}), 400

    image = request.files["image"]
    buffer = image.read()

    async def convert():
        try:
            colorify = ColorifyAI()
            result = await colorify.image2sketch(buffer)
            return jsonify({ "status": 200, "result": result })
        except Exception as e:
            return jsonify({ "status": 500, "msg": f"Terjadi kesalahan: {str(e)}" }), 500

    return asyncio.run(convert())


app = app
