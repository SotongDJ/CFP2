import tomlkit, json
print("----\nStart export")
print("    ----")
print("    load data")
title_dict = tomlkit.load(open("blg/mid/annotation.toml"))
keyword_doc = tomlkit.load(open("blg/keyword.toml"))
header_list = ["name", "apple", "google", "spotify", "youtube", "image", "feed"]
title_list = list()
total_int = len(title_dict.keys())
print("    ----")
print("    export docs/blg-playlist")
playlist_dict = dict()
for enum_int, value_dict in enumerate(title_dict.values()):
    key_inner_str = "time{}".format(total_int-enum_int)
    value_inner_dict = {header_str:value_dict.get(header_str,"") for header_str in header_list}
    tag_list = value_dict.get("tag",list())
    category_list = [n for n in value_dict.get("category",list()) if n[0] != "#"]
    tag_list.extend(sorted(list(set(category_list))))
    deduplicate_tag_list = list()
    for tag in tag_list:
        if tag not in deduplicate_tag_list:
            deduplicate_tag_list.append(tag)
    value_inner_dict["tag"] = deduplicate_tag_list
    playlist_dict[key_inner_str] = value_inner_dict

with open("docs/blg-playlist.json",'w') as target_handler:
    json.dump(playlist_dict,target_handler,indent=0,sort_keys=True)
with open("docs/blg-playlist.toml",'w') as target_handler:
    tomlkit.dump(playlist_dict,target_handler)

print("    ----")
print("    export docs/blg-tag_class")
tag2class_dict = {tag_name: [str(n) for n in entry_detail["category"]] for tag_name, entry_detail in keyword_doc.items()}

with open("docs/blg-tag_class.json",'w') as target_handler:
    json.dump(tag2class_dict,target_handler,indent=0,sort_keys=True)
with open("docs/blg-tag_class.toml",'w') as target_handler:
    tomlkit.dump(tag2class_dict,target_handler)

print("    ----")
print("    export docs/blg-class_tag")
class2tag_dict = dict()
for tag_name, entry_detail in keyword_doc.items():
    for category_name in entry_detail["category"]:
        category_list = class2tag_dict.get(str(category_name),list())
        category_list.append(tag_name)
        class2tag_dict[str(category_name)] = category_list

with open("docs/blg-class_tag.json",'w') as target_handler:
    json.dump(class2tag_dict,target_handler,indent=0,sort_keys=True)
with open("docs/blg-class_tag.toml",'w') as target_handler:
    tomlkit.dump(class2tag_dict,target_handler)

print("    ----\nEnd export")
