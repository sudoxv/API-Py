from flask import Flask, jsonify, request
from Scrapers.CheckResi import CheckResi
from Scrapers.FluxImage import Flux
from Scrapers.QwenAI import Qwen
from Scrapers.Otakudesu import Otakudesu

app = Flask(__name__)

@app.route("/")
def index():
    return "Hello, World!"

@app.route("/api/otakudesu/sedang-tayang", methods=["GET"])
def otakudesu_route():
    data = Otakudesu()
    return jsonify({
        "status": 200,
        "author": "Nakaa",
        "result": data
    }), 200

@app.route("/api/cekresi", methods=["GET"])
def cekresi_route():
    try:
        nomer_resi = request.args.get("nomer_resi")
        ekspedisi = request.args.get("ekspedisi")
        if not nomer_resi:
            return jsonify({
                "status": 401,
                "author": "Nakaa",
                "msg": "Parameter 'nomer_resi' not found"            }), 401
        if not ekspedisi:
            return jsonify({
                "status": 401,
                "author": "Nakaa",
                "msg": " Parameter 'ekspedisi' not found"
            }), 401

        result = CheckResi(nomer_resi, ekspedisi)
        return jsonify({
            "status": 200,
            "author": "Nakaa",
            "result": result
        }), 200

    except ValueError as e:
        return jsonify({
            "status": 400,
            "author": "Nakaa",
            "msg": str(e)
        }), 400
    except Exception as e:
        return jsonify({
            "status": 500,
            "author": "Nakaa",
            "msg": str(e)
        }), 500

@app.route("/api/ai/flux-image", methods=["GET"])
def flux_route():
    prompt = request.args.get("prompt")
    if not prompt:
        return jsonify({
            "status": 401,
            "author": "Nakaa",
            "msg": "Parameter 'prompt' not found"
        }), 401
    else:
        try:
            flux = Flux(prompt)
            result = flux.generate()
            return jsonify({
                "status": 200,
                "author": "Nakaa",
                "result": result
            }), 200
        except Exception as e:
            return jsonify({
                "status": 500,
                "author": "Nakaa",
                "msg": str(e)
            }), 500

@app.route("/api/ai/qwen-chat", methods=["GET"])
def qwen_route():
    prompt = request.args.get("prompt")
    system = request.args.get("system")
    session_hash = request.args.get("session_hash")
    if not prompt:
        return jsonify({
            "status": 401,
            "author": "Nakaa",
            "msg": "Parameter 'prompt' not found"
        }), 401
    else:
        try:
            qwen = Qwen(prompt, system, session_hash)
            result = qwen.generate()
            return jsonify({
                "status": 200,
                "author": "Nakaa",
                "result": result
            }), 200
        except Exception as e:
            return jsonify({
                "status": 500,
                "author": "Nakaa",
                "msg": str(e)
            }), 500

app = app
