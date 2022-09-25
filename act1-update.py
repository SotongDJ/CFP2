from bs4 import BeautifulSoup as bs
from PIL import Image
import json, tomlkit, requests, pathlib, hashlib, time
print("Start collection")
result_dict = dict()
print("    ----")
print("    Start collection: Feed")
print("        Feed: grab rss feed")
rss_req = requests.get("https://feeds.buzzsprout.com/1974862.rss")
print("        Feed: convert XML and update dictionary")
rss_feed = bs(rss_req.text,"xml")
rss_dict = dict()
name2url_dict = dict()
url2file_dict = dict()
if pathlib.Path("blg/record/image.toml").exists():
    img_doc = tomlkit.load(open("blg/record/image.toml"))
    name2url_dict.update({str(x):str(y) for x,y in img_doc["name2url"].items()})  # type: ignore
    url2file_dict.update({str(x):str(y) for x,y in img_doc["url2file"].items()})  # type: ignore
img_str = rss_feed.find("image").url.contents[0]  # type: ignore
img_size_list = [96,128,192,256,384,512]
for unit in rss_feed.find_all('item'):
    name = unit.title.contents[0]
    url = unit.enclosure['url']
    rss_dict[name] = url
    img_list = [ufa["href"] for ufa in unit.find_all('itunes:image')] + [img_str]
    img_url = img_list[0]
    name2url_dict[name] = img_url
    if img_url not in url2file_dict.keys():
        print(F"request: {img_url} for {name}")
        cover_img_r = requests.get(img_url, stream=True)
        time.sleep(1)
        cover_img_r.raw.decode_content = True
        cover_img = Image.open(cover_img_r.raw)
        h = hashlib.new('sha256')
        h.update(cover_img.tobytes())
        img_name = h.hexdigest()
        url2file_dict[img_url] = img_name
        if not pathlib.Path(F"docs/p/{img_name}/512.png").exists():
            print(F"resize: docs/p/{img_name}")
            for img_size in img_size_list:
                pathlib.Path(F"docs/p/{img_name}/").mkdir(parents=True,exist_ok=True)
                wpercent = (img_size / float(cover_img.size[0]))
                hsize = int((float(cover_img.size[1]) * float(wpercent)))
                cover_img_res = cover_img.resize((img_size, hsize), Image.Resampling.LANCZOS)
                cover_img_res.save(F"docs/p/{img_name}/{img_size}.png")
result_dict["feed"] = rss_dict
with open("blg/record/feedPodcastRequests.xml","w") as xmlf:
    xmlf.write(rss_req.text)
with open("blg/record/feedPodcast.toml","w") as tomlf:
    tomlkit.dump(rss_dict,tomlf)
with open("blg/record/image.toml","w") as tomlf:
    tomlkit.dump({"name2url":name2url_dict,"url2file":url2file_dict},tomlf)
print("    Finish collection: Feed")
#
print("    ----")
print("    Start collection: Apple")
print("        Feed: grab rss feed")
apple_req = requests.get("https://podcasts.apple.com/tw/podcast/%E7%99%BE%E9%9D%88%E6%9E%9C-news/id1106847606")
print("        Feed: convert HTML and update dictionary")
apple_track = bs(apple_req.text,"lxml").find('ol',{'class':'tracks tracks--linear-show'})
if pathlib.Path("blg/record/ApplePodcast.toml").exists():
    apple_doc = tomlkit.load(open("blg/record/ApplePodcast.toml"))
    apple_record = {str(x):str(y) for x,y in apple_doc.items()}
else:
    apple_record = dict()
apple_dict = dict()
for unit in apple_track.find_all('a',{"class":"link tracks__track__link--block"}):  # type: ignore
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
with open("blg/record/ApplePodcastRequests.html","w") as xmlf:
    xmlf.write(apple_req.text)
with open("blg/record/ApplePodcast.toml","w") as tomlf:
    tomlkit.dump(apple_dict,tomlf)
print("    Finish collection: Apple")
#
print("    ----")
print("    Start collection: Google")
print("        Feed: grab rss feed")
google_req = requests.get("https://podcasts.google.com/feed/aHR0cHM6Ly9mZWVkcy5zb3VuZGNsb3VkLmNvbS91c2Vycy9zb3VuZGNsb3VkOnVzZXJzOjIyMTM2MTk4MC9zb3VuZHMucnNz")
google_track = bs(google_req.text,"lxml").find('div',{'jsname':'quCAxd'})
print("        Feed: convert HTML and update dictionary")
google_dict = dict()
for unit in google_track.find_all('a'):  # type: ignore
    url = unit['href'].split("?sa=")[0].replace("./","https://podcasts.google.com/")
    name = unit.findChildren("div", {'class': 'e3ZUqe'})[0].contents[0]
    google_dict[name] = url
result_dict["google"] = google_dict
with open("blg/record/GooglePodcastRequests.html","w") as xmlf:
    xmlf.write(google_req.text)
with open("blg/record/GooglePodcast.toml","w") as tomlf:
    tomlkit.dump(google_dict,tomlf)
print("    Finish collection: Google")
#
print("    ----")
print("    Start collection: Spotify")
if pathlib.Path("secret.toml").exists():
    print("        Feed: grab rss feed")
    secret_docs = tomlkit.load(open("secret.toml"))
    spotify_auth_url = 'https://accounts.spotify.com/api/token'
    spotify_auth_response = requests.post(spotify_auth_url, {
        'grant_type': 'client_credentials',
        'client_id': secret_docs['spotify_id'],
        'client_secret': secret_docs['spotify_secret'],
    })
    spotify_auth_response_dict = spotify_auth_response.json()
    spotify_access_token = spotify_auth_response_dict['access_token']
    spotify_url = "https://api.spotify.com/v1/shows/5Vv32KtHB3peVZ8TeacUty/episodes?market=TW&limit=50"
    spotify_headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Authorization": "Bearer {}".format(spotify_access_token),
    }
    spotify_req = requests.get(spotify_url, headers=spotify_headers)
    with open("blg/record/SpotifyPodcastRequests.json","w") as xmlf:
        xmlf.write(spotify_req.text)
    print("        Feed: convert JSON and update dictionary")
    spotify_req_dict = json.loads(spotify_req.text)
    if pathlib.Path("blg/record/SpotifyPodcast.toml").exists():
        spotify_doc = tomlkit.load(open("blg/record/SpotifyPodcast.toml"))
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
    with open("blg/record/SpotifyPodcast.toml","w") as tomlf:
        tomlkit.dump(spotify_dict,tomlf)
else:
    print("        Skip: secret not found")
print("    Finish collection: Spotify")
#
print("    ----")
print("    Start collection: YouTube")
print("        Feed: grab rss feed")
youtube_req = requests.get("https://www.youtube.com/feeds/videos.xml?channel_id=UCD2KoUc0f4Bv2Bz0mbOah8g")
youtube_track = bs(youtube_req.text,"xml")
print("        Feed: convert XML and update dictionary")
if pathlib.Path("blg/record/YouTube.toml").exists():
    youtube_doc = tomlkit.load(open("blg/record/YouTube.toml"))
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
with open("blg/record/YouTubeRequests.xml","w") as xmlf:
    xmlf.write(youtube_req.text)
with open("blg/record/YouTube.toml","w") as tomlf:
    tomlkit.dump(youtube_dict,tomlf)
print("    Finish collection: YouTube")
#
with open("blg/mid/history.toml",'w') as target_handler:
    tomlkit.dump(result_dict,target_handler)
print("    ----\nFinish collection")
