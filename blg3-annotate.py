import tomlkit, re
print("----\nStart annotation")
structure_doc = tomlkit.load(open("blg/mid/structure.toml"))
keyword_doc = tomlkit.load(open("blg/keyword.toml"))
def check(input_str,exclude,do_re=str()):
    include_list = list()
    exclude_list = list()
    for key_str in structure_doc.keys():
        include_bool = (input_str in key_str)
        if do_re != str():
            key_re = re.compile(do_re)
            if key_re.match(key_str):
                include_bool = True
        if include_bool:
            exclude_bool = False
            for exclude_str in exclude:
                if exclude_str in key_str:
                    exclude_bool = True
            if exclude_bool:
                exclude_list.append(key_str)
            else:
                include_list.append(key_str)
    return include_list, exclude_list
for entry_name, entry_detail in keyword_doc.items():
    inclusive_collect_list = list()
    exclusive_collect_list = list()
    for inclusive_str in entry_detail['inclusive']:
        inclusive_list, exclusive_list = check(inclusive_str,entry_detail['exclusive'],do_re=entry_detail.get('re',str()))
        inclusive_collect_list.extend([n for n in inclusive_list if n not in inclusive_collect_list])
        exclusive_collect_list.extend([n for n in exclusive_list if n not in exclusive_collect_list])
    if len(inclusive_collect_list) > 1:
        print(F"[{entry_name}]\n  found in: ({len(inclusive_collect_list)})")
        print("    {}".format("\n    ".join(inclusive_collect_list)))
        print(F"  Excluded: ({len(exclusive_collect_list)})")
        print("    {}".format("\n    ".join(exclusive_collect_list)))
    for episode_str in inclusive_collect_list:
        episode_table = structure_doc[episode_str]
        episode_tag_list = episode_table["tag"]  # type: ignore
        episode_tag_list.append(entry_name)  # type: ignore
        episode_table["tag"] = episode_tag_list  # type: ignore
        episode_tag_list = episode_table["category"]  # type: ignore
        episode_tag_list.extend(entry_detail["category"])  # type: ignore
        episode_table["category"] = episode_tag_list  # type: ignore
        structure_doc[episode_str] = episode_table
with open("blg/mid/annotation.toml",'w') as target_handler:
    tomlkit.dump(structure_doc,target_handler)
print("    ----\nEnd annotation")