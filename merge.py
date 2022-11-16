import argparse,tomlkit,pathlib
class config:
    def __init__(self,inputStr):
        self.prefix = inputStr
        self.dict = dict()
        self.dict.update(dict(tomlkit.load(open(inputStr+"/config.toml"))))
        self.youtube = self.dict.get("youtube","")
        self.correct = self.dict.get("correct",dict())
        pathlib.Path(args.target+"/record/").mkdir(parents=True,exist_ok=True)
        pathlib.Path(args.target+"/mid/").mkdir(parents=True,exist_ok=True)
    def xmlw(self,contentStr,partStr):
        with open(self.prefix+partStr,"w") as target_handler:
            target_handler.write(contentStr)
    def toml(self,inputDict,partStr):
        with open(self.prefix+partStr,'w') as target_handler:
            tomlkit.dump(inputDict,target_handler)

parser = argparse.ArgumentParser(description="Update data")
parser.add_argument("target", help="target path")
args = parser.parse_args()

Config = config(args.target)
print("----\nStart merge")
result_doc = tomlkit.load(open(args.target+"/mid/history.toml"))
month_doc = tomlkit.load(open(args.target+"/record/feedPodcast-month.toml"))
alias_doc = tomlkit.load(open(args.target+"/alias.toml"))
img_doc = tomlkit.load(open(args.target+"/record/image.toml"))
name2url_dict = {str(x):str(y) for x,y in img_doc["name2url"].items()} # type: ignore
url2file_dict = {str(x):str(y) for x,y in img_doc["url2file"].items()} # type: ignore
def correct(input_str):
    replace_str = input_str
    for from_str, to_str in Config.correct.items():
        replace_str = replace_str.replace(from_str,to_str)
    output_str = " ".join([n for n in replace_str.split(" ") if n != ""])
    if output_str in alias_doc.keys():
        output_str = alias_doc[output_str]
    splitAt_str = output_str.split("@")[0]  # type: ignore
    shrink_str = " ".join([n for n in splitAt_str.split(" ") if n != ""])
    return output_str, shrink_str
title_dict = dict()
for podcast_str, podcast_dict in result_doc.items():
    for title_str,link_str in podcast_dict.items():
        name_str, id_str = correct(title_str)
        title_episode_dict = title_dict.get(id_str,dict())
        title_episode_dict['name'] = sorted([title_episode_dict.get('name',""),name_str], key=lambda x:len(x))[-1]  # type: ignore
        title_episode_dict[podcast_str] = link_str
        title_dict[id_str] = title_episode_dict
for title_str,link_str in name2url_dict.items():
    name_str, id_str = correct(title_str)
    title_episode_dict = title_dict.get(id_str,dict())
    title_episode_dict["image"] = url2file_dict[link_str]
    title_dict[id_str] = title_episode_dict
for title_str,month_str in month_doc.items():
    name_str, id_str = correct(title_str)
    title_episode_dict = title_dict.get(id_str,dict())
    title_episode_dict["tag"] = [month_str]
    title_dict[id_str] = title_episode_dict
annotation = tomlkit.document()
annotation.add(tomlkit.comment("Add your own tag to each episode"))
annotation.add(tomlkit.nl())
youtube_entities = tomlkit.document()
if Config.youtube != "":
    youtube_entities.add(tomlkit.comment("Need to clear for act4"))
    youtube_entities.add(tomlkit.nl())
    for title_str, link_dict in title_dict.items():
        episode = tomlkit.table()
        episode.update(link_dict)
        if "feed" in link_dict.keys():
            annotation[title_str] = episode
            episode["category"] = list()
        else:
            episode["tag"] = list()
            episode["category"] = list()
            youtube_entities[title_str] = episode
Config.toml(annotation,"/mid/structure.toml")
if Config.youtube != "":
    Config.xmlw("".join(["\"{}\"\n".format(n["name"]) for n in annotation.values() if "youtube" not in n.keys()]),"/mid/list_lack_youtube.txt")
    Config.toml(youtube_entities,"/mid/youtube_extra.toml")
    Config.xmlw("".join(["\"{}\"\n".format(n["name"]) for n in youtube_entities.values()]),"/mid/list_youtube_only.txt")
print("    ----\nEnd merge")
