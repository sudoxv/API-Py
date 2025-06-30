from bs4 import BeautifulSoup
import requests

def Otakudesu():
    url = "https://otakudesu.cloud"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    ven = soup.find("div", class_="venz")
    ttl = ven.find_all("div", class_="thumb")
    epsd = ven.find_all("div", class_="epz")
    schdl = ven.find_all("div", class_="epztipe")
    updt = ven.find_all("div", class_="newnime")

    img_src = [link.get("src") for link in ven.find_all("img") if link.get("src")]
    a_href = [link.get("href") for link in ven.find_all("a") if link.get("href")]
    title_text = [e.text.strip() if e else "none" for e in ttl] + ["none"] * (len(img_src) - len(ttl))
    epsd_text = [e.text.strip() if e else "none" for e in epsd] + ["none"] * (len(img_src) - len(epsd))
    schdl_text = [e.text.strip() if e else "none" for e in schdl] + ["none"] * (len(img_src) - len(schdl))
    updt_text = [e.text.strip() if e else "none" for e in updt] + ["none"] * (len(img_src) - len(updt))

    return [{ "title": title, "img": img, "href": a, "episode": episode, "schedule": schedule, "update": update } for title, img, a, episode, schedule, update in zip(title_text, img_src, a_href, epsd_text, schdl_text, updt_text)]
