#!/bin/env python
"""Update RSS feed."""
from datetime import datetime
import argparse
import hashlib
import json
import pathlib
import time
from io import BytesIO
from PIL import Image
from bs4 import BeautifulSoup as bs
import random
import requests
import rtoml
import configdo

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/603.3.8 (KHTML, like Gecko) Version/10.1.2 Safari/603.3.8",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36",
    "Mozilla/5.0 (iPad; CPU OS 10_3_3 like Mac OS X) AppleWebKit/603.3.8 (KHTML, like Gecko) Version/10.0 Mobile/14G60 Safari/602.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:61.0) Gecko/20100101 Firefox/61.0",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:55.0) Gecko/20100101 Firefox/55.0",
    "Mozilla/5.0 (Linux; Android 7.0; SM-G930V Build/NRD90M) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.125 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 6.0.1; Nexus 5X Build/MMB29P) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.96 Mobile Safari/537.36 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
    "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/7046A194A",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.86 Safari/537.36 Edge/13.10586",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36",
    "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36"
]

def do_job(target_str,configing):
    """Main thread"""
    result_dict = {}
    print("Start collection")
    print("    ----")
    print("    Start collection: Feed")
    print("        Feed: grab rss feed")
    headers = {'User-Agent': random.choice(user_agents)} 
    print(headers)
    rss_req = requests.get(configing.rss,timeout=60,headers=headers)
    rss_req.encoding = 'utf-8'
    print("        Feed: convert XML and update dictionary")
    rss_feed = bs(rss_req.content,"xml")
    rss_dict = {}
    description_dict = {}
    month_dict = {}
    name2url_dict = {}
    url_to_file_dict = {}
    if pathlib.Path(target_str+"/record/image.toml").exists():
        img_doc = rtoml.load(open(target_str+"/record/image.toml",encoding="utf8"))
        name2url_dict.update(img_doc["name2url"])
        url_to_file_dict.update(img_doc["url2file"])
    channel_cover_str = rss_feed.find("image").url.contents[0]  # type: ignore
    img_size_list = [96,128,192,256,384,512]
    if pathlib.Path(target_str+"/record/description.toml").exists():
        description_path = target_str+"/record/description.toml"
        description_dict.update(rtoml.load(open(description_path,encoding="utf8")))
    for unit in rss_feed.find_all('item'):
        name = unit.title.contents[0]
        url = unit.enclosure['url']
        unit_description = unit.description
        contents = unit_description.contents
        description = str(contents[0]) if len(contents) > 0 else ""
        rss_dict[name] = url
        if name not in description_dict:
            description_dict[name] = description
        original_time_str = unit.pubDate.contents[0].replace('GMT', '+0000')
        mthfmt_str = "%a, %d %b %Y %H:%M:%S %z"
        month_str = datetime.strptime(original_time_str,mthfmt_str).strftime("%b %Y")
        month_dict[name] = month_str
        img_list = [ufa["href"] for ufa in unit.find_all('itunes:image')] + [channel_cover_str]
        img_url = str(img_list[0])
        name2url_dict[name] = img_url
        path_name_str = pathlib.Path(img_url).parent.name
        file_name_str = pathlib.Path(img_url).name
        safe_img_url = F"{path_name_str}-{file_name_str}"
        if safe_img_url not in url_to_file_dict:
            print(F"request: {img_url} for '{name}'")
            cover_img_r = requests.get(img_url,stream=True,timeout=60)
            # content_type = cover_img_r.headers.get('Content-Type')
            time.sleep(1)
            if cover_img_r.text[:5] != "<?xml":
                cover_img_r.raw.decode_content = True
                img_file = BytesIO(cover_img_r.content)
                cover_img = Image.open(img_file)
                h_name = hashlib.new('sha256')
                h_name.update(cover_img.tobytes())
                img_name = h_name.hexdigest()
            else:
                print("            Access Denied to the file")
                print("            Use default img instead")
                img_name = "e5b8c2da7e6ce54bd780a0030714a67b9bc6cd9da84bc993e5cad3238463ecd6"
            url_to_file_dict[safe_img_url] = img_name
            if not pathlib.Path(F"docs/p/{img_name}/512.png").exists():
                print(F"resize: docs/p/{img_name}")
                for img_size in img_size_list:
                    pathlib.Path(F"docs/p/{img_name}/").mkdir(parents=True,exist_ok=True)
                    wpercent = img_size / float(cover_img.size[0])
                    hsize = int((float(cover_img.size[1]) * float(wpercent)))
                    cover_img_res = cover_img.resize((img_size, hsize), Image.Resampling.LANCZOS)
                    cover_img_res.save(F"docs/p/{img_name}/{img_size}.png")
    result_dict["feed"] = rss_dict
    configing.xmlw(rss_req.text,"/record/feedPodcastRequests.xml")
    configing.toml(rss_dict,"/record/feedPodcast.toml")
    configing.toml(month_dict,"/record/feedPodcast-month.toml")
    configing.toml(description_dict,"/record/description.toml")
    configing.toml({"name2url":name2url_dict,"url2file":url_to_file_dict},"/record/image.toml")
    print("    Finish collection: Feed")
    #
    if configing.apple != "":
        print("    ----")
        print("    Start collection: Apple")
        print("        Feed: grab rss feed")
        apple_req = requests.get(configing.apple,timeout=60)
        apple_req.encoding = 'utf-8'
        print("        Feed: convert HTML and update dictionary")
        apple_track = bs(apple_req.content,"lxml").find('ol',{'class':'tracks tracks--linear-show'})
        if pathlib.Path(target_str+"/record/ApplePodcast.toml").exists():
            apple_doc = rtoml.load(open(target_str+"/record/ApplePodcast.toml",encoding="utf8"))
            apple_record = {str(x):str(y) for x,y in apple_doc.items()}
        else:
            apple_record = {}
        apple_dict = {}
        apple_tag = {"class":"link tracks__track__link--block"}
        for unit in apple_track.find_all('a',apple_tag):  # type: ignore
            name_wt_hidden = unit.contents[0].replace(" &ZeroWidthSpace;","")
            name_single = name_wt_hidden.replace("\n","")
            name = " ".join([n for n in name_single.split(" ") if n != ""])
            url = unit['href']
            if name in apple_record.keys():
                if apple_record[name] != url:
                    print("ERROR: Duplicate entry no consistent, value:", url, apple_record[name])
            else:
                apple_dict[name] = url
        apple_dict.update(apple_record)
        result_dict["apple"] = apple_dict
        configing.xmlw(apple_req.text,"/record/ApplePodcastRequests.html")
        configing.toml(apple_dict,"/record/ApplePodcast.toml")
        print("    Finish collection: Apple")
    #
    if configing.google != "":
        print("    ----")
        print("    Start collection: Google")
        print("        Feed: grab rss feed")
        google_req = requests.get(configing.google,timeout=60)
        google_req.encoding = 'utf-8'
        google_track = bs(google_req.content,"lxml").find('div',{'jsname':'quCAxd'})
        print("        Feed: convert HTML and update dictionary")
        if pathlib.Path(target_str+"/record/GooglePodcast.toml").exists():
            google_doc = rtoml.load(open(target_str+"/record/GooglePodcast.toml",encoding="utf8"))
            google_record = {str(x):str(y) for x,y in google_doc.items()}
        else:
            google_record = {}
        google_dict = {}
        for unit in google_track.find_all('a'):  # type: ignore
            url = unit['href'].split("?sa=")[0].replace("./","https://podcasts.google.com/")
            name = unit.findChildren("div", {'class': 'e3ZUqe'})[0].contents[0]
            if name in google_record.keys():
                if google_record[name] != url:
                    print("ERROR: Duplicate entry no consistent, value:", url, google_record[name])
            else:
                google_dict[name] = url
        google_dict.update(google_record)
        result_dict["google"] = google_dict
        configing.xmlw(google_req.text,"/record/GooglePodcastRequests.html")
        configing.toml(google_dict,"/record/GooglePodcast.toml")
        print("    Finish collection: Google")
    #
    if configing.spotify != "":
        print("    ----")
        print("    Start collection: Spotify")
        spotify_toml_name = target_str+"/record/SpotifyPodcast.toml"
        if pathlib.Path("secret.toml").exists():
            print("        Feed: grab rss feed")
            secret_docs = rtoml.load(open("secret.toml",encoding="utf8"))
            spotify_auth_url = 'https://accounts.spotify.com/api/token'
            spotify_config = {
                'grant_type': 'client_credentials',
                'client_id': secret_docs['spotify_id'],
                'client_secret': secret_docs['spotify_secret'],
            }
            spotify_auth_response = requests.post(spotify_auth_url,spotify_config,timeout=60)
            spotify_auth_response_dict = spotify_auth_response.json()
            spotify_access_token = spotify_auth_response_dict['access_token']
            spotify_url = configing.spotify
            spotify_headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": F"Bearer {spotify_access_token}",
            }
            spotify_req = requests.get(spotify_url,headers=spotify_headers,timeout=60)
            spotify_req.encoding = 'utf-8'
            configing.xmlw(spotify_req.text,"/record/SpotifyPodcastRequests.json")
            print("        Feed: convert JSON and update dictionary")
            spotify_req_dict = json.loads(spotify_req.content)
            if pathlib.Path(spotify_toml_name).exists():
                spotify_doc = rtoml.load(open(spotify_toml_name,encoding="utf8"))
                spotify_record = {str(x):str(y) for x,y in spotify_doc.items()}
            else:
                spotify_record = {}
            spotify_dict = {}
            for unit_dict in spotify_req_dict["items"]:
                sp_dict = {}
                sp_dict[0] = "https://api.spotify.com/v1/episodes/"
                sp_dict[1] = "https://open.spotify.com/episode/"
                url = unit_dict['href'].replace(sp_dict[0],sp_dict[1])
                name_wt_hidden = unit_dict['name'].replace(" &ZeroWidthSpace;","")
                name_single = name_wt_hidden.replace("\n","")
                name_str = " ".join([n for n in name_single.split(" ") if n != ""])
                if name_str in spotify_record.keys():
                    record_name = spotify_record[name_str]
                    if record_name != url:
                        print(F"ERROR: Duplicate entry no consistent, value: {url} {record_name}")
                else:
                    spotify_dict[name_str] = url
            spotify_dict.update(spotify_record)
            result_dict["spotify"] = spotify_dict
            configing.toml(spotify_dict,"/record/SpotifyPodcast.toml")
        else:
            print("        Skip: secret not found")
            print("        Feed: use old records")
            if pathlib.Path(spotify_toml_name).exists():
                spotify_doc = rtoml.load(open(spotify_toml_name,encoding="utf8"))
                spotify_record = {str(x):str(y) for x,y in spotify_doc.items()}
            else:
                spotify_record = {}
            spotify_dict = {}
            spotify_dict.update(spotify_record)
            result_dict["spotify"] = spotify_dict
        print("    Finish collection: Spotify")
    #
    if configing.youtube != "":
        print("    ----")
        print("    Start collection: YouTube")
        print("        Feed: grab rss feed")
        youtube_req = requests.get(configing.youtube,timeout=60)
        youtube_req.encoding = 'utf-8'
        youtube_track = bs(youtube_req.content,"xml")
        print("        Feed: convert XML and update dictionary")
        if pathlib.Path(target_str+"/record/YouTube.toml").exists():
            youtube_doc = rtoml.load(open(target_str+"/record/YouTube.toml",encoding="utf8"))
            youtube_record = {str(x):str(y) for x,y in youtube_doc.items()}
        else:
            youtube_record = {}
        youtube_dict = {}
        for unit in youtube_track.find_all('entry'):
            name = unit.title.contents[0]
            url = unit.link['href']
            if name in youtube_record.keys():
                if youtube_record[name] != url:
                    print("ERROR: Duplicate entry no consistent, value:", url, youtube_record[name])
            else:
                youtube_dict[name] = url
        youtube_dict.update(youtube_record)
        result_dict["youtube"] = youtube_dict
        configing.xmlw(youtube_req.text,"/record/YouTubeRequests.xml")
        configing.toml(youtube_dict,"/record/YouTube.toml")
        print("    Finish collection: YouTube")
    #
    configing.toml(result_dict,"/mid/history.toml")
    print("    ----\nFinish collection")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update data")
    parser.add_argument("target", help="target path")
    args = parser.parse_args()
    configin = configdo.ConfigCla(args.target)  # type: ignore
    do_job(args.target,configin)
