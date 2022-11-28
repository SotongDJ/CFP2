import rtoml, argparse #, json
from datetime import datetime

def convertMonth(input):
    return int(datetime.strptime(input,"%b %Y").strftime("%Y%m"))

parser = argparse.ArgumentParser(description="Export playlist")
parser.add_argument("target", help="target path")
args = parser.parse_args()

print("----\nStart export")
print("    ----")
print("    load data")
title_dict = rtoml.load(open(args.target+"/mid/annotation.toml"))
keyword_doc = rtoml.load(open(args.target+"/mid/keyword.toml"))
month_doc = rtoml.load(open(args.target+"/record/feedPodcast-month.toml"))
month_dict = {m:datetime.strptime(m,"%b %Y").strftime("%Y") for m in month_doc.values()}
reverse_month_dict = dict()
for month_str, year_str in month_dict.items():
    year_list = reverse_month_dict.get(year_str,list())
    year_list.append(month_str)
    reverse_month_dict[year_str] = year_list
reverse_dict = {y:sorted(reverse_month_dict[y],key=lambda m : convertMonth(m)) for y in sorted(list(reverse_month_dict.keys()),key=lambda x : int(x), reverse=True)}
month_list = sorted(list(month_dict.keys()), key=lambda m : convertMonth(m), reverse=True)
header_list = ["name", "apple", "google", "spotify", "youtube", "image", "feed"]
title_list = list()
total_int = len(title_dict.keys())
print("    ----")
print("    export docs/"+args.target+"-playlist")
playlist_dict = dict()
for enum_int, value_dict in enumerate(title_dict.values()):
    key_inner_str = "time{}".format(total_int-enum_int)
    value_inner_dict = {header_str:value_dict.get(header_str,"") for header_str in header_list}
    value_inner_list = ["\"{}\": \"{}\"".format(header_str,value_dict.get(header_str,"")) for header_str in header_list]
    value_inner_str = "\"time{}\":".format(total_int-enum_int) + "{\n" + ",\n".join(value_inner_list)
    tag_list = value_dict.get("tag",list())
    category_list = [n for n in value_dict.get("category",list()) if n[0] != "#"]
    tag_list.extend(sorted(list(set(category_list))))
    deduplicate_tag_list = list()
    for tag in tag_list:
        if tag not in deduplicate_tag_list:
            deduplicate_tag_list.append(tag)
    value_inner_dict["tag"] = deduplicate_tag_list
    playlist_dict[key_inner_str] = value_inner_dict
    value_inner_str = value_inner_str + ",\n\"tag\": {}".format(deduplicate_tag_list)
    title_list.append(value_inner_str)
outer_str = "const playlist = {\n"+"\n},\n".join(title_list)+"\n}\n};\n"

# with open("docs/blg-playlist.json",'w') as target_handler:
#     json.dump(playlist_dict,target_handler,indent=0,sort_keys=True)
# with open("docs/blg-playlist.toml",'w') as target_handler:
#     rtoml.dump(playlist_dict,target_handler)

print("    ----")
print("    export docs/"+args.target+"-tag_class")
tag2class_dict = {tag_name: [str(n) for n in entry_detail["category"]] for tag_name, entry_detail in keyword_doc.items()}
tag2class_dict.update({m: [F"#{y}"] for m,y in month_dict.items()})
tag2class_list = ["\"{}\": {}".format(tag_name,tag_category_list) for tag_name, tag_category_list in tag2class_dict.items()]
tag2class_str = "const tag_class = {\n"+",\n".join(tag2class_list)+"\n};\n"

# with open("docs/blg-tag_class.json",'w') as target_handler:
#     json.dump(tag2class_dict,target_handler,indent=0,sort_keys=True)
# with open("docs/blg-tag_class.toml",'w') as target_handler:
#     rtoml.dump(tag2class_dict,target_handler)

print("    ----")
print("    export docs/"+args.target+"-class_tag")
class2tag_dict = dict()
class2tag_dict.update({F"#{y}":m for y,m in reverse_dict.items()})
for tag_name, entry_detail in keyword_doc.items():
    for category_name in entry_detail["category"]:
        category_list = class2tag_dict.get(str(category_name),list())
        category_list.append(tag_name)
        class2tag_dict[str(category_name)] = category_list
class2tag_list = list()
for category_name, category_list in class2tag_dict.items():
    class2tag_list.append("\"{}\": {}".format(category_name,category_list))
class2tag_str = "const class_tag = {\n"+",\n".join(class2tag_list)+"\n};\n"

# with open("docs/blg-class_tag.json",'w') as target_handler:
#     json.dump(class2tag_dict,target_handler,indent=0,sort_keys=True)
# with open("docs/blg-class_tag.toml",'w') as target_handler:
#     rtoml.dump(class2tag_dict,target_handler)

with open("docs/"+args.target+"-playlist.js",'w') as target_handler:
    target_handler.write(outer_str)
    target_handler.write(tag2class_str)
    target_handler.write(class2tag_str)
print("    ----\nEnd export")
