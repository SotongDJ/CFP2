"""Configuration"""
import pathlib
import rtoml

class ConfigCla:
    """Configuration class"""
    def __init__(self,input_str:str):
        self.prefix = input_str
        self.dict = dict()
        self.dict.update(dict(rtoml.load(open(input_str+"/config.toml",encoding="utf8"))))
        self.rss = self.dict["rss"]
        self.apple = self.dict.get("apple","")
        self.google = self.dict.get("google","")
        self.spotify = self.dict.get("spotify","")
        self.youtube = self.dict.get("youtube","")
        self.correct = self.dict.get("correct",dict())
        pathlib.Path(input_str+"/record/").mkdir(parents=True,exist_ok=True)
        pathlib.Path(input_str+"/mid/").mkdir(parents=True,exist_ok=True)
    def xmlw(self,content_str:str,part_str:str):
        """Export as plain text"""
        with open(self.prefix+part_str,"w",encoding="utf8") as target_handler:
            target_handler.write(content_str)
    def toml(self,input_dict:dict,part_str:str,note=""):
        """Export as toml"""
        with open(self.prefix+part_str,"w",encoding="utf8") as target_handler:
            target_handler.write(note)
        with open(self.prefix+part_str,"a",encoding="utf8") as target_handler:
            rtoml.dump(input_dict,target_handler)
