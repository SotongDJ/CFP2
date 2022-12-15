"""Export playlist"""
import argparse
import json
from datetime import datetime
import rtoml

def convert_month(input_str):
    """get month tag"""
    return int(datetime.strptime(input_str,"%b %Y").strftime("%Y%m"))

def do_job(target_str):
    """Main thread"""
    print("----\nStart export")
    print("    ----")
    print("    load data")
    title_fn_str = target_str+"/mid/annotation.toml"
    title_doc = rtoml.load(open(title_fn_str,encoding="utf8"))
    keyword_fn_str = target_str+"/mid/keyword.toml"
    keyword_doc = rtoml.load(open(keyword_fn_str,encoding="utf8"))
    month_fn_str = target_str+"/record/feedPodcast-month.toml"
    month_doc = rtoml.load(open(month_fn_str,encoding="utf8"))
    month_dict = {m:datetime.strptime(m,"%b %Y").strftime("%Y") for m in month_doc.values()}
    rvs_m_dict = {} # reverse_month_dict
    for month_str, year_str in month_dict.items():
        year_list = rvs_m_dict.get(year_str,[])
        year_list.append(month_str)
        rvs_m_dict[year_str] = year_list
    reverse_list = sorted(list(rvs_m_dict.keys()),key=int, reverse=True)
    reverse_dict = {y:sorted(rvs_m_dict[y],key=convert_month) for y in reverse_list}
    # month_list = sorted(list(month_dict.keys()), key=convert_month, reverse=True)
    header_dict = {
        "name":"",
        "feed":"",
        "image":"",
        "tag":[],
        "description":"",
        "extra":{},
        "apple":"",
        "google":"",
        "spotify":"",
        "youtube":""
    }
    # title_list = []
    # total_int = len(title_doc.keys())
    print("    ----")
    print("    export docs/"+target_str+"-playlist")
    playlist_dict = {}
    for key_str, value_dict in title_doc.items():
        value_inner_dict = {x:value_dict.get(x,y) for x,y in header_dict.items()}
        tag_list = value_dict.get("tag",[])
        category_list = [n for n in value_dict.get("category",[]) if n[0] != "#"]
        tag_list.extend(sorted(list(set(category_list))))
        deduplicate_tag_list = []
        for tag in tag_list:
            if tag not in deduplicate_tag_list:
                deduplicate_tag_list.append(tag)
        value_inner_dict["tag"] = deduplicate_tag_list
        playlist_dict[key_str] = value_inner_dict
    outer_str = "const playlist = "+json.dumps(playlist_dict,indent=0,ensure_ascii=True)+";\n"

    # with open("docs/blg-playlist.json","w") as target_handler:
    #     json.dump(playlist_dict,target_handler,indent=0,sort_keys=True)
    with open("docs/blg-playlist.toml","w") as target_handler:
        rtoml.dump(playlist_dict,target_handler)

    print("    ----")
    print("    export docs/"+target_str+"-tag_class")
    tag_to_class_dict = {x: [str(n) for n in y["category"]] for x, y in keyword_doc.items()}
    tag_to_class_dict.update({m: [F"#{y}"] for m,y in month_dict.items()})
    tag_to_class_list = [F"\"{x}\": {y}" for x, y in tag_to_class_dict.items()]
    tag_to_class_str = "const tag_class = {\n"+",\n".join(tag_to_class_list)+"\n};\n"

    # with open("docs/blg-tag_class.json","w") as target_handler:
    #     json.dump(tag_to_class_dict,target_handler,indent=0,sort_keys=True)
    # with open("docs/blg-tag_class.toml","w") as target_handler:
    #     rtoml.dump(tag_to_class_dict,target_handler)

    print("    ----")
    print("    export docs/"+target_str+"-class_tag")
    class_to_tag_dict = {}
    class_to_tag_dict.update({F"#{y}":m for y,m in reverse_dict.items()})
    for tag_name, entry_detail in keyword_doc.items():
        for category_name in entry_detail["category"]:
            category_list = class_to_tag_dict.get(str(category_name),[])
            category_list.append(tag_name)
            class_to_tag_dict[str(category_name)] = category_list
    class_to_tag_list = []
    for category_name, category_list in class_to_tag_dict.items():
        class_to_tag_list.append(F"\"{category_name}\": {category_list}")
    class_to_tag_str = "const class_tag = {\n"+",\n".join(class_to_tag_list)+"\n};\n"

    # with open("docs/blg-class_tag.json","w") as target_handler:
    #     json.dump(class_to_tag_dict,target_handler,indent=0,sort_keys=True)
    # with open("docs/blg-class_tag.toml","w") as target_handler:
    #     rtoml.dump(class_to_tag_dict,target_handler)

    with open("docs/"+target_str+"-playlist.js","w",encoding="utf8") as target_handler:
        target_handler.write(outer_str)
        target_handler.write(tag_to_class_str)
        target_handler.write(class_to_tag_str)
    print("    ----\nEnd export")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export playlist")
    parser.add_argument("target", help="target path")
    args = parser.parse_args()
    do_job(args.target)
