import tomlkit
print("----\nStart export")
title_dict = tomlkit.load(open("mid/annotation.toml"))
keyword_doc = tomlkit.load(open("keyword.toml"))
header_list = ["name", "apple", "google", "spotify", "youtube", "image", "feed"]
title_list = list()
total_int = len(title_dict.keys())
for enum_int, value_dict in enumerate(title_dict.values()):
    value_inner_list = ["\"{}\": \"{}\"".format(header_str,value_dict.get(header_str,"")) for header_str in header_list]
    value_inner_str = "\"time{}\":".format(total_int-enum_int) + "{\n" + ",\n".join(value_inner_list)
    tag_list = value_dict.get("tag",list())
    category_list = [n for n in value_dict.get("category",list()) if n[0] != "#"]
    tag_list.extend(sorted(list(set(category_list))))
    deduplicate_tag_list = list()
    for tag in tag_list:
        if tag not in deduplicate_tag_list:
            deduplicate_tag_list.append(tag)
    value_inner_str = value_inner_str + ",\n\"tag\": {}".format(deduplicate_tag_list)
    title_list.append(value_inner_str)
outer_str = "const playlist = {\n"+"\n},\n".join(title_list)+"\n}\n};\n"

tag2class_dict = {tag_name: [str(n) for n in entry_detail["category"]] for tag_name, entry_detail in keyword_doc.items()}
tag2class_list = ["\"{}\": {}".format(tag_name,tag_category_list) for tag_name, tag_category_list in tag2class_dict.items()]
tag2class_str = "const tag_class = {\n"+",\n".join(tag2class_list)+"\n};\n"

class2tag_dict = dict()
for tag_name, entry_detail in keyword_doc.items():
    for category_name in entry_detail["category"]:
        category_list = class2tag_dict.get(str(category_name),list())
        category_list.append(tag_name)
        class2tag_dict[str(category_name)] = category_list
class2tag_list = list()
for category_name, category_list in class2tag_dict.items():
    class2tag_list.append("\"{}\": {}".format(category_name,category_list))
class2tag_str = "const class_tag = {\n"+",\n".join(class2tag_list)+"\n};\n"

with open("docs/playlist.js",'w') as target_handler:
    target_handler.write(outer_str)
    target_handler.write(tag2class_str)
    target_handler.write(class2tag_str)
print("    ----\nEnd export")
