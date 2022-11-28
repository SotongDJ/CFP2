import argparse,rtoml
from configdo import config

parser = argparse.ArgumentParser(description="Update data")
parser.add_argument("target", help="target path")
args = parser.parse_args()

Config = config(args.target)
print("----\nStart merge")
result_doc = rtoml.load(open(args.target+"/mid/history.toml"))
month_doc = rtoml.load(open(args.target+"/record/feedPodcast-month.toml"))
alias_doc = rtoml.load(open(args.target+"/alias.toml"))
img_doc = rtoml.load(open(args.target+"/record/image.toml"))
name2url_dict = {str(x):str(y) for x,y in img_doc["name2url"].items()} # type: ignore
url2file_dict = {str(x):str(y) for x,y in img_doc["url2file"].items()} # type: ignore
def correct(input_str):
    replace_str = input_str
    for from_str, to_str in Config.correct.items():
        replace_str = replace_str.replace(from_str,to_str)
    output_str = " ".join([n for n in replace_str.split(" ") if n != ""])
    if output_str in alias_doc.keys():
        output_str = alias_doc[output_str]
    splitAt_str = output_str.split("@")[0]
    shrink_str = " ".join([n for n in splitAt_str.split(" ") if n != ""])
    return output_str, shrink_str
title_dict = dict()
print("    ----")
print("    collect podcast info from history.toml")
for podcast_str, podcast_dict in result_doc.items():
    for title_str,link_str in podcast_dict.items():
        name_str, id_str = correct(title_str)
        title_episode_dict = title_dict.get(id_str,dict())
        title_episode_dict['name'] = sorted([title_episode_dict.get('name',""),name_str], key=lambda x:len(x))[-1]
        title_episode_dict[podcast_str] = link_str
        title_dict[id_str] = title_episode_dict
print("    ----")
print("    collect podcast info from image.toml")
for title_str,link_str in name2url_dict.items():
    name_str, id_str = correct(title_str)
    title_episode_dict = title_dict.get(id_str,dict())
    title_episode_dict["image"] = url2file_dict[link_str]
    title_dict[id_str] = title_episode_dict
print("    ----")
print("    collect podcast info from feedPodcast-month.toml")
for title_str,month_str in month_doc.items():
    name_str, id_str = correct(title_str)
    title_episode_dict = title_dict.get(id_str,dict())
    title_episode_dict["tag"] = [month_str]
    title_dict[id_str] = title_episode_dict
# annotation = rtoml.document()
# annotation.add(rtoml.comment("Add your own tag to each episode"))
# annotation.add(rtoml.nl())
# youtube_entities = rtoml.document()
# youtube_entities.add(rtoml.comment("Need to clear for act4"))
# youtube_entities.add(rtoml.nl())
annotation = dict()
youtube_entities = dict()
print("    ----")
print("    collect annotation")
for title_str, link_dict in title_dict.items():
    # episode = rtoml.table()
    episode = dict()
    episode.update(link_dict)
    if "feed" in link_dict.keys():
        episode["category"] = list()
        annotation[title_str] = episode
    else:
        youtube_entities[title_str] = episode
Config.toml(annotation,"/mid/structure.toml",note="# Add your own tag to each episode\n\n")
if Config.youtube != "":
    print("    ----")
    print("    export list_lack_youtube and youtube_extra")
    Config.xmlw("".join(["\"{}\"\n".format(n["name"]) for n in annotation.values() if "youtube" not in n.keys()]),"/mid/list_lack_youtube.txt")
    Config.toml(youtube_entities,"/mid/youtube_extra.toml",note="# Need to clear for annotate.py\n\n")
    Config.xmlw("".join(["\"{}\"\n".format(n["name"]) for n in youtube_entities.values()]),"/mid/list_youtube_only.txt")
print("    ----\nEnd merge")
