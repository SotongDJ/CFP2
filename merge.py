import argparse,rtoml
from configdo import config

parser = argparse.ArgumentParser(description="Update data")
parser.add_argument("target", help="target path")
args = parser.parse_args()

Config = config(args.target)
print("----\nStart merge")
result_doc = rtoml.load(open(args.target+"/mid/history.toml"))
month_doc = rtoml.load(open(args.target+"/record/feedPodcast-month.toml"))
name2id_dict = {}
alias_doc = rtoml.load(open(args.target+"/alias.toml"))
img_doc = rtoml.load(open(args.target+"/record/image.toml"))
name2url_dict = img_doc["name2url"]
url2file_dict = img_doc["url2file"]
def adjust(input_str):
    replace_str = input_str
    for from_str, to_str in Config.correct.items():
        replace_str = replace_str.replace(from_str,to_str)
    output_str = " ".join([n for n in replace_str.split(" ") if n != ""])
    return output_str
def correct(input_str,max_int=0):
    max_len_int = len(str(max_int))
    replace_str = adjust(input_str)
    if alias_doc.get(replace_str,"") != "":
        id_str = alias_doc[replace_str]
        name2id_dict[replace_str] = id_str
    elif replace_str not in name2id_dict.keys():
        current_int = len(name2id_dict)+1
        current_len_int = len(str(current_int))
        addup_str = "0"*(max_len_int-current_len_int)
        id_str = "time{}".format(addup_str+str(current_int))
        name2id_dict[replace_str] = id_str
    else:
        id_str = name2id_dict[replace_str]
    return id_str
title_dict = {}
print("    ----")
print("    collect podcast info from history.toml")
for podcast_str, podcast_dict in result_doc.items():
    title_list = [n for n in podcast_dict.keys()]
    title_list_int = len(title_list)
    for index_int in range(title_list_int):
        title_str = title_list[title_list_int-index_int-1]
        link_str = podcast_dict[title_str]
        id_str = correct(title_str,max_int=title_list_int)
        time_str = id_str.replace("extra","time")
        title_episode_dict = title_dict.get(time_str,{})
        if "extra" in id_str:
            name_dict = title_episode_dict.get("extra",{})
            name_dict[adjust(title_str)] = link_str
            title_episode_dict["extra"] = name_dict
        else:
            name_list = title_episode_dict.get("names",[])
            name_list.append(adjust(title_str))
            names_list = sorted(list(set(name_list)), key=lambda x:len(x))
            title_episode_dict["names"] = names_list
            title_episode_dict["name"] = names_list[-1]
            title_episode_dict[podcast_str] = link_str
        title_dict[time_str] = title_episode_dict
print("    ----")
print("    collect podcast info from image.toml")
for title_str,link_str in name2url_dict.items():
    id_str = correct(title_str)
    title_episode_dict = title_dict.get(id_str,{})
    safeImg_url = "{}-{}".format(Path(link_str).parent.name,Path(link_str).name)
    title_episode_dict["image"] = url2file_dict[safeImg_url]
    title_dict[id_str] = title_episode_dict
print("    ----")
print("    collect podcast info from feedPodcast-month.toml")
for title_str,month_str in month_doc.items():
    id_str = correct(title_str)
    title_episode_dict = title_dict.get(id_str,{})
    title_episode_dict["tag"] = [month_str]
    title_dict[id_str] = title_episode_dict
# annotation = rtoml.document()
# annotation.add(rtoml.comment("Add your own tag to each episode"))
# annotation.add(rtoml.nl())
# youtube_entities = rtoml.document()
# youtube_entities.add(rtoml.comment("Need to clear for act4"))
# youtube_entities.add(rtoml.nl())
# episode = rtoml.table()
annotation = {}
youtube_entities = {}
print("    ----")
print("    collect annotation")
for title_str, link_dict in title_dict.items():
    episode = {}
    episode.update(link_dict)
    if "feed" in link_dict.keys():
        episode["category"] = []
        annotation[title_str] = episode
    else:
        youtube_entities[title_str] = episode
reverse_dict = {n:annotation[n] for n in sorted(annotation.keys(),reverse=True)}
Config.toml(reverse_dict,"/mid/structure.toml",note="# Add your own tag to each episode\n\n")
if Config.youtube != "":
    print("    ----")
    print("    export list_lack_youtube and youtube_extra")
    # Config.toml(youtube_entities,"/mid/youtube_extra.toml",note="# Need to clear for annotate.py\n\n")
    Config.xmlw("".join(["\"{}\"\n".format(n["name"]) for n in annotation.values() if "youtube" not in n.keys()]),"/mid/list_lack_youtube.txt")
    Config.toml({n["name"]:"extra" for n in youtube_entities.values()},"/mid/list_youtube_only.toml")
print("    ----\nEnd merge")
