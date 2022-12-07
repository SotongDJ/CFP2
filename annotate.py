"""Annotate structural file"""
import argparse
import re
import pathlib
import rtoml

def do_job(target_str):
    """Main thread"""
    print("----\nStart annotation")
    structure_doc = rtoml.load(open(target_str+"/mid/structure.toml",encoding="utf8"))
    keyword_dict = {}
    keyword_list = []
    for keyword_path in sorted(list(pathlib.Path(target_str).glob('keyword-*.toml'))):
        keyword_doc = rtoml.load(open(keyword_path,encoding="utf8"))
        unique_list = [n for n in keyword_doc.keys() if n not in keyword_list]
        duplicate_list = [n for n in keyword_doc.keys() if n in keyword_list]
        if len(duplicate_list) > 0:
            print(F"ERROR: duplicate list ~ {duplicate_list}")
        keyword_list.extend(unique_list)
        keyword_dict.update(keyword_doc)
    def check(input_str,exclude,do_re=str()):
        include_list = []
        exclude_list = []
        for key_str,detail_dict in structure_doc.items():
            name_str = detail_dict["name"]
            include_bool = (input_str in name_str)
            if do_re != str():
                key_re = re.compile(do_re)
                if key_re.match(name_str):
                    include_bool = True
            if include_bool:
                exclude_bool = False
                for exclude_str in exclude:
                    if exclude_str in name_str:
                        exclude_bool = True
                if exclude_bool:
                    exclude_list.append(key_str)
                else:
                    include_list.append(key_str)
        return include_list, exclude_list
    for entry_name in keyword_list:
        ent_de = keyword_dict[entry_name] # entry_detail
        inc_col_list = [] # inclusive_collect_list
        exc_col_list = [] # exclusive_collect_list
        for inc_str in ent_de['inclusive']: # inclusive_str
            inc_list, exc_list = check(inc_str,ent_de['exclusive'],do_re=ent_de.get('re',str()))
            inc_col_list.extend([n for n in inc_list if n not in inc_col_list])
            exc_col_list.extend([n for n in exc_list if n not in exc_col_list])
        if len(inc_col_list) > 1:
            print(F"[{entry_name}]\n  found in: ({len(inc_col_list)})")
            print("    {}".format("\n    ".join(inc_col_list)))
            print(F"  Excluded: ({len(exc_col_list)})")
            print("    {}".format("\n    ".join(exc_col_list)))
        for episode_str in inc_col_list:
            episode_table = structure_doc[episode_str]
            episode_tag_list = episode_table["tag"]
            episode_tag_list.append(entry_name)
            episode_table["tag"] = episode_tag_list
            episode_tag_list = episode_table["category"]
            episode_tag_list.extend(ent_de["category"])
            episode_table["category"] = episode_tag_list
            structure_doc[episode_str] = episode_table
    with open(target_str+"/mid/keyword.toml","w",encoding="utf8") as target_handler:
        rtoml.dump(keyword_dict,target_handler)
    with open(target_str+"/mid/annotation.toml","w",encoding="utf8") as target_handler:
        target_handler.write("# Add your own tag to each episode\n\n")
    with open(target_str+"/mid/annotation.toml","a",encoding="utf8") as target_handler:
        rtoml.dump(structure_doc,target_handler)
    print("    ----\nEnd annotation")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Annotate data")
    parser.add_argument("target", help="target path")
    args = parser.parse_args()
    do_job(args.target)
