import rtoml,pathlib

class config:
    def __init__(self,inputStr):
        self.prefix = inputStr
        self.dict = dict()
        self.dict.update(dict(rtoml.load(open(inputStr+"/config.toml"))))
        self.rss = self.dict["rss"]
        self.apple = self.dict.get("apple","")
        self.google = self.dict.get("google","")
        self.spotify = self.dict.get("spotify","")
        self.youtube = self.dict.get("youtube","")
        self.correct = self.dict.get("correct",dict())
        pathlib.Path(inputStr+"/record/").mkdir(parents=True,exist_ok=True)
        pathlib.Path(inputStr+"/mid/").mkdir(parents=True,exist_ok=True)
    def xmlw(self,contentStr,partStr):
        with open(self.prefix+partStr,"w") as target_handler:
            target_handler.write(contentStr)
    def toml(self,inputDict,partStr,note=""):
        with open(self.prefix+partStr,'w') as target_handler:
            target_handler.write(note)
        with open(self.prefix+partStr,'a') as target_handler:
            rtoml.dump(inputDict,target_handler)
