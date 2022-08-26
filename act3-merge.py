import tomlkit
print("----\nStart merge")
result_doc = tomlkit.load(open("mid/history.toml"))
alias_doc = tomlkit.load(open("alias.toml"))
image_doc = tomlkit.load(open("data/image.toml"))
def correct(input_str):
    replace_str = input_str.replace("\u200b","").replace("啦‍♂️、","啦🙅‍♂️、")
    output_str = " ".join([n for n in replace_str.split(" ") if n != ""])
    if output_str in alias_doc.keys():
        output_str = alias_doc[output_str]
    splitAt_str = output_str.split("@")[0]
    shrink_str = " ".join([n for n in splitAt_str.split(" ") if n != ""])
    return output_str, shrink_str
title_dict = dict()
for podcast_str, podcast_dict in result_doc.items():
    for title_str,link_str in podcast_dict.items():
        name_str, id_str = correct(title_str)
        title_episode_dict = title_dict.get(id_str,dict())
        title_episode_dict['name'] = sorted([title_episode_dict.get('name',""),name_str], key=lambda x:len(x))[-1]
        title_episode_dict[podcast_str] = link_str
        title_dict[id_str] = title_episode_dict
for title_str,link_str in image_doc.items():
    name_str, id_str = correct(title_str)
    title_episode_dict = title_dict.get(id_str,dict())
    title_episode_dict["image"] = link_str
    title_dict[id_str] = title_episode_dict
annotation = tomlkit.document()
annotation.add(tomlkit.comment("Add your own tag to each episode"))
annotation.add(tomlkit.nl())
youtube_entities = tomlkit.document()
youtube_entities.add(tomlkit.comment("Need to clear for act4"))
youtube_entities.add(tomlkit.nl())
for title_str, link_dict in title_dict.items():
    episode = tomlkit.table()
    episode.update(link_dict)
    episode["tag"] = list()
    episode["category"] = list()
    if "feed" in link_dict.keys():
        annotation[title_str] = episode
    else:
        youtube_entities[title_str] = episode
with open("mid/structure.toml",'w') as target_handler:
    tomlkit.dump(annotation,target_handler)
with open("mid/list_lack_youtube.txt","w") as target_handler:
    target_handler.write("".join(["\"{}\"\n".format(n["name"]) for n in annotation.values() if "youtube" not in n.keys()]))
with open("mid/youtube_extra.toml",'w') as target_handler:
    tomlkit.dump(youtube_entities,target_handler)
with open("mid/list_youtube_only.txt","w") as target_handler:
    target_handler.write("".join(["\"{}\"\n".format(n["name"]) for n in youtube_entities.values()]))
print("    ----\nEnd merge")
