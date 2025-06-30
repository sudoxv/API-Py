from flask import Flask, jsonify, request
import requests
from bs4 import BeautifulSoup
from Crypto.Cipher import AES
import base64
import random
import string
import re
from otakudesu import Otakudesu
from cekresi import Cekresi

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
    nomer_resi = request.args.get("nomer_resi")
    ekspedisi = request.args.get("ekspedisi")
    if not nomer_resi:
        return jsonify({ "status": 400, "msg": 'Parameter "nomer_resi" tidak dapat ditemukan' }), 400
    if not ekspedisi:
        return jsonify({ "status": 401, "msg": 'Parameter "ekspedisi" tidak dapat ditemukan' })
    else:
        data = Cekresi(nomer_resi, ekspedisi)
        return jsonify({ "status": 200, "result": data }), 200

if __name__ == "__main__":
    app.run(port=8080)
