from bs4 import BeautifulSoup as bs
from PIL import Image
from datetime import datetime
import json,rtoml,requests,pathlib,hashlib,time,argparse
from configdo import config

parser = argparse.ArgumentParser(description="Update data")
parser.add_argument("target", help="target path")
args = parser.parse_args()

Config = config(args.target)
result_dict = dict()
print("Start collection")
print("    ----")
print("    Start collection: Feed")
print("        Feed: grab rss feed")
rss_req = requests.get(Config.rss)
print("        Feed: convert XML and update dictionary")
rss_feed = bs(rss_req.text,"xml")
rss_dict = dict()
month_dict = dict()
name2url_dict = dict()
url2file_dict = dict()
if pathlib.Path(args.target+"/record/image.toml").exists():
    img_doc = rtoml.load(open(args.target+"/record/image.toml"))
    name2url_dict.update(img_doc["name2url"])
    url2file_dict.update(img_doc["url2file"])
channelCover_str = rss_feed.find("image").url.contents[0]
img_size_list = [96,128,192,256,384,512]
for unit in rss_feed.find_all('item'):
    name = unit.title.contents[0]
    url = unit.enclosure['url']
    rss_dict[name] = url
    original_time_str = unit.pubDate.contents[0]
    month_str = datetime.strptime(original_time_str,"%a, %d %b %Y %H:%M:%S %z").strftime("%b %Y")
    month_dict[name] = month_str
    img_list = [ufa["href"] for ufa in unit.find_all('itunes:image')] + [channelCover_str]
    img_url = img_list[0]
    name2url_dict[name] = img_url
    safeImg_url = "{}-{}".format(pathlib.Path(img_url).parent.name,pathlib.Path(img_url).name)
    if safeImg_url not in url2file_dict.keys():
        print(F"request: {img_url} for {name}")
        cover_img_r = requests.get(img_url, stream=True)
        time.sleep(1)
        cover_img_r.raw.decode_content = True
        cover_img = Image.open(cover_img_r.raw)
        h = hashlib.new('sha256')
        h.update(cover_img.tobytes())
        img_name = h.hexdigest()
        url2file_dict[safeImg_url] = img_name
        if not pathlib.Path(F"docs/p/{img_name}/512.png").exists():
            print(F"resize: docs/p/{img_name}")
            for img_size in img_size_list:
                pathlib.Path(F"docs/p/{img_name}/").mkdir(parents=True,exist_ok=True)
                wpercent = (img_size / float(cover_img.size[0]))
                hsize = int((float(cover_img.size[1]) * float(wpercent)))
                cover_img_res = cover_img.resize((img_size, hsize), Image.Resampling.LANCZOS)
                cover_img_res.save(F"docs/p/{img_name}/{img_size}.png")
result_dict["feed"] = rss_dict
Config.xmlw(rss_req.text,"/record/feedPodcastRequests.xml")
Config.toml(rss_dict,"/record/feedPodcast.toml")
Config.toml(month_dict,"/record/feedPodcast-month.toml")
Config.toml({"name2url":name2url_dict,"url2file":url2file_dict},"/record/image.toml")
print("    Finish collection: Feed")
#
if Config.apple != "":
    print("    ----")
    print("    Start collection: Apple")
    print("        Feed: grab rss feed")
    apple_req = requests.get(Config.apple)
    print("        Feed: convert HTML and update dictionary")
    apple_track = bs(apple_req.text,"lxml").find('ol',{'class':'tracks tracks--linear-show'})
    if pathlib.Path(args.target+"/record/ApplePodcast.toml").exists():
        apple_doc = rtoml.load(open(args.target+"/record/ApplePodcast.toml"))
        apple_record = {str(x):str(y) for x,y in apple_doc.items()}
    else:
        apple_record = dict()
    apple_dict = dict()
    for unit in apple_track.find_all('a',{"class":"link tracks__track__link--block"}):
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
    Config.xmlw(apple_req.text,"/record/ApplePodcastRequests.html")
    Config.toml(apple_dict,"/record/ApplePodcast.toml")
    print("    Finish collection: Apple")
#
if Config.google != "":
    print("    ----")
    print("    Start collection: Google")
    print("        Feed: grab rss feed")
    google_req = requests.get(Config.google)
    google_track = bs(google_req.text,"lxml").find('div',{'jsname':'quCAxd'})
    print("        Feed: convert HTML and update dictionary")
    google_dict = dict()
    for unit in google_track.find_all('a'):
        url = unit['href'].split("?sa=")[0].replace("./","https://podcasts.google.com/")
        name = unit.findChildren("div", {'class': 'e3ZUqe'})[0].contents[0]
        google_dict[name] = url
    result_dict["google"] = google_dict
    Config.xmlw(google_req.text,"/record/GooglePodcastRequests.html")
    Config.toml(google_dict,"/record/GooglePodcast.toml")
    print("    Finish collection: Google")
#
if Config.spotify != "":
    print("    ----")
    print("    Start collection: Spotify")
    if pathlib.Path("secret.toml").exists():
        print("        Feed: grab rss feed")
        secret_docs = rtoml.load(open("secret.toml"))
        spotify_auth_url = 'https://accounts.spotify.com/api/token'
        spotify_auth_response = requests.post(spotify_auth_url, {
            'grant_type': 'client_credentials',
            'client_id': secret_docs['spotify_id'],
            'client_secret': secret_docs['spotify_secret'],
        })
        spotify_auth_response_dict = spotify_auth_response.json()
        spotify_access_token = spotify_auth_response_dict['access_token']
        spotify_url = Config.spotify
        spotify_headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer {}".format(spotify_access_token),
        }
        spotify_req = requests.get(spotify_url, headers=spotify_headers)
        Config.xmlw(spotify_req.text,"/record/SpotifyPodcastRequests.json")
        print("        Feed: convert JSON and update dictionary")
        spotify_req_dict = json.loads(spotify_req.text)
        if pathlib.Path(args.target+"/record/SpotifyPodcast.toml").exists():
            spotify_doc = rtoml.load(open(args.target+"/record/SpotifyPodcast.toml"))
            spotify_record = {str(x):str(y) for x,y in spotify_doc.items()}
        else:
            spotify_record = dict()
        spotify_dict = dict()
        for unit_dict in spotify_req_dict["items"]:
            url = unit_dict['href'].replace("https://api.spotify.com/v1/episodes/","https://open.spotify.com/episode/")
            name_wt_hidden = unit_dict['name'].replace(" &ZeroWidthSpace;","")
            name_single = name_wt_hidden.replace("\n","")
            name = " ".join([n for n in name_single.split(" ") if n != ""])
            if name in spotify_record.keys():
                if spotify_record[name] != url:
                    print("ERROR: Duplicate entry no consistent, value:", url, spotify_record[name])
            else:
                spotify_dict[name] = url
        spotify_dict.update(spotify_record)
        result_dict["spotify"] = spotify_dict
        Config.toml(spotify_dict,"/record/SpotifyPodcast.toml")
    else:
        print("        Skip: secret not found")
        print("        Feed: use old records")
        if pathlib.Path(args.target+"/record/SpotifyPodcast.toml").exists():
            spotify_doc = rtoml.load(open(args.target+"/record/SpotifyPodcast.toml"))
            spotify_record = {str(x):str(y) for x,y in spotify_doc.items()}
        else:
            spotify_record = dict()
        spotify_dict = dict()
        spotify_dict.update(spotify_record)
        result_dict["spotify"] = spotify_dict
    print("    Finish collection: Spotify")
#
if Config.youtube != "":
    print("    ----")
    print("    Start collection: YouTube")
    print("        Feed: grab rss feed")
    youtube_req = requests.get(Config.youtube)
    youtube_track = bs(youtube_req.text,"xml")
    print("        Feed: convert XML and update dictionary")
    if pathlib.Path(args.target+"/record/YouTube.toml").exists():
        youtube_doc = rtoml.load(open(args.target+"/record/YouTube.toml"))
        youtube_record = {str(x):str(y) for x,y in youtube_doc.items()}
    else:
        youtube_record = dict()
    youtube_dict = dict()
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
    Config.xmlw(youtube_req.text,"/record/YouTubeRequests.xml")
    Config.toml(youtube_dict,"/record/YouTube.toml")
    print("    Finish collection: YouTube")
#
Config.toml(result_dict,"/mid/history.toml")
print("    ----\nFinish collection")
