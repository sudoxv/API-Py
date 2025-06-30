import requests
from bs4 import BeautifulSoup
from Crypto.Cipher import AES
import base64
import random
import string
import re

def pad_pkcs7(data):
    pad_len = 16 - len(data) % 16
    return data + bytes([pad_len] * pad_len)

def create_timers(resi):
    key_hex = "79540e250fdb16afac03e19c46dbdeb3"
    iv_hex = "eb2bb9425e81ffa942522e4414e95bd0"
    key = bytes.fromhex(key_hex)
    iv = bytes.fromhex(iv_hex)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded_data = pad_pkcs7(resi.encode('utf-8'))
    encrypted = cipher.encrypt(padded_data)
    return base64.b64encode(encrypted).decode('utf-8')

def Cekresi(noresi, ekspedisi):
    ekspedisi_map = {
        'shopee-express': 'SPX',
        'ninja': 'NINJA',
        'lion-parcel': 'LIONPARCEL',
        'pos-indonesia': 'POS',
        'tiki': 'TIKI',
        'acommerce': 'ACOMMERCE',
        'gtl-goto-logistics': 'GTL',
        'paxel': 'PAXEL',
        'sap-express': 'SAP',
        'indah-logistik-cargo': 'INDAH',
        'lazada-express-lex': 'LEX',
        'lazada-logistics': 'LEL',
        'janio-asia': 'JANIO',
        'jet-express': 'JETEXPRESS',
        'pcp-express': 'PCP',
        'pt-ncs': 'NCS',
        'nss-express': 'NSS',
        'grab-express': 'GRAB',
        'rcl-red-carpet-logistics': 'RCL',
        'qrim-express': 'QRIM',
        'ark-xpress': 'ARK',
        'standard-express-lwe': 'LWE',
        'luar-negeri-bea-cukai': 'BEACUKAI'
    }

    if not noresi:
        raise ValueError("Nomor resi diperlukan")
    if ekspedisi not in ekspedisi_map:
        raise ValueError(f"List ekspedisi yang tersedia: {', '.join(ekspedisi_map.keys())}")

    resi_clean = noresi.upper().replace(' ', '')
    response = requests.get("https://cekresi.com/")
    soup = BeautifulSoup(response.text, 'html.parser')

    viewstate = soup.select_one('input[name="viewstate"]')['value']
    secret_key = soup.select_one('input[name="secret_key"]')['value']
    timers = create_timers(resi_clean)

    form_data = {
        'viewstate': viewstate,
        'secret_key': secret_key,
        'e': ekspedisi_map[ekspedisi],
        'noresi': resi_clean,
        'timers': timers
    }

    random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=7))
    post_url = f"https://apa2.cekresi.com/cekresi/resi/initialize.php?ui=e0ad7e971ce77822056ba7a155f85c11&p=1&w={random_string}"

    headers = {
        'content-type': 'application/x-www-form-urlencoded',
        'referer': 'https://cekresi.com/',
        'origin': 'https://cekresi.com',
        'user-agent': 'Mozilla/5.0'
    }

    post_response = requests.post(post_url, data=form_data, headers=headers)
    soup_res = BeautifulSoup(post_response.text, 'html.parser')

    result = {
        "success": False,
        "message": "",
        "data": {
            "resi": noresi,
            "ekspedisi": "",
            "ekspedisiCode": ekspedisi_map[ekspedisi],
            "status": "",
            "tanggalKirim": "",
            "customerService": "",
            "lastPosition": "",
            "shareLink": "",
            "history": []
        }
    }

    alert_success = soup_res.select_one('.alert.alert-success')
    if alert_success:
        result["success"] = True
        result["message"] = alert_success.text.strip()
        ekspedisi_name = soup_res.select_one('#nama_expedisi')
        if ekspedisi_name:
            result["data"]["ekspedisi"] = ekspedisi_name.text.strip()

        for row in soup_res.select('table.table-striped tbody tr'):
            tds = row.select('td')
            if len(tds) >= 3:
                label = tds[0].text.strip()
                value = tds[2].text.strip()
                if label == 'Tanggal Pengiriman':
                    result["data"]["tanggalKirim"] = value
                elif label == 'Status':
                    result["data"]["status"] = value

        for h5 in soup_res.find_all('h5'):
            if 'Customer Service Phone:' in h5.text:
                result["data"]["customerService"] = h5.text.replace('Customer Service Phone:', '').strip()
                break

        last_position = soup_res.select_one('#last_position')
        if last_position:
            result["data"]["lastPosition"] = last_position.text.strip()

        share_link = soup_res.select_one('#linkcekresi')
        if share_link:
            result["data"]["shareLink"] = share_link.get('value', '')

        history_section = soup_res.find('h4', string=re.compile("History"))
        if history_section:
            for row in history_section.find_next('table').select('tbody tr')[1:]:
                tds = row.select('td')
                if len(tds) >= 2:
                    tanggal = tds[0].text.strip()
                    keterangan = tds[1].text.strip()
                    result["data"]["history"].append({
                        "tanggal": tanggal,
                        "keterangan": keterangan
                    })

    else:
        alert_error = soup_res.select_one('.alert.alert-danger, .alert.alert-warning')
        result["message"] = alert_error.text.strip() if alert_error else 'Tidak dapat mengambil informasi resi'

    return { "msg": result["message"], "data": result["data"] }
