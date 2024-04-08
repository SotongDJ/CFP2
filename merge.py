"""Merge different sources into single structural file"""
import argparse
from pathlib import Path
import rtoml
import configdo

def do_job(target_str,configing):
    """Main thread"""
    print("----\nStart merge")
    result_doc = rtoml.load(open(target_str+"/mid/history.toml",encoding="utf8"))
    month_doc = rtoml.load(open(target_str+"/record/feedPodcast-month.toml",encoding="utf8"))
    dscri_doc = rtoml.load(open(target_str+"/record/description.toml",encoding="utf8"))
    name2id_dict = {}
    alias_doc = rtoml.load(open(target_str+"/alias.toml",encoding="utf8"))
    img_doc = rtoml.load(open(target_str+"/record/image.toml",encoding="utf8"))
    name2url_dict = img_doc["name2url"]
    url2file_dict = img_doc["url2file"]
    def adjust(input_str):
        replace_str = input_str
        for from_str, to_str in configing.correct.items():
            replace_str = replace_str.replace(from_str,to_str)
        output_str = " ".join([n for n in replace_str.split(" ") if n != ""])
        return output_str
    def correct(input_str,max_int=0):
        max_len_int = len(str(max_int))
        replace_str = adjust(input_str)
        if alias_doc.get(replace_str,"") != "":
            id_str = alias_doc[replace_str]
            name2id_dict[replace_str] = id_str
        elif replace_str not in name2id_dict:
            current_int = len(name2id_dict)+1
            current_len_int = len(str(current_int))
            addup_str = "0"*(max_len_int-current_len_int)
            id_str = F"time{addup_str}{current_int}"
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
                names_list = sorted(list(set(name_list)), key=len)
                title_episode_dict["names"] = names_list
                title_episode_dict["name"] = names_list[0]
                title_episode_dict[podcast_str] = link_str
            title_dict[time_str] = title_episode_dict
    print("    ----")
    print("    collect podcast info from image.toml")
    for title_str,link_str in name2url_dict.items():
        id_str = correct(title_str)
        title_episode_dict = title_dict.get(id_str,{})
        path_name_str = Path(link_str).parent.name
        file_name_str = Path(link_str).name
        safe_img_url = F"{path_name_str}-{file_name_str}"
        title_episode_dict["image"] = url2file_dict[safe_img_url]
        title_dict[id_str] = title_episode_dict
    print("    ----")
    print("    collect podcast info from feedPodcast-month.toml")
    for title_str,month_str in month_doc.items():
        id_str = correct(title_str)
        title_episode_dict = title_dict.get(id_str,{})
        title_episode_dict["tag"] = [month_str]
        title_dict[id_str] = title_episode_dict
    print("    ----")
    print("    collect podcast info from description.toml")
    for title_str,dscri_str in dscri_doc.items():
        id_str = correct(title_str)
        title_episode_dict = title_dict.get(id_str,{})
        title_episode_dict["description"] = dscri_str
        title_dict[id_str] = title_episode_dict
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
    configing.toml(reverse_dict,"/mid/structure.toml",note="# Add your own tag to each episode\n\n")
    if configing.youtube != "":
        print("    ----")
        print("    export list_lack_youtube and youtube_extra")
        # configing.toml(
        #   youtube_entities,
        #   "/mid/youtube_extra.toml",
        #   note="# Need to clear for annotate.py\n\n"
        # )
        anntt_list = annotation.values()
        lack_fn_str = "/mid/list_lack_youtube.txt"
        lack_content = ["\""+n["name"]+"\"\n" for n in anntt_list if "youtube" not in n.keys()]
        configing.xmlw("".join(lack_content),lack_fn_str)
        only_fn_str = "/mid/list_youtube_only.toml"
        configing.toml({n["name"]:"extra" for n in youtube_entities.values() if 'name' in n.keys()},only_fn_str)
    print("    ----\nEnd merge")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Merge data")
    parser.add_argument("target", help="target path")
    args = parser.parse_args()
    configin = configdo.ConfigCla(args.target)  # type: ignore
    do_job(args.target,configin)
