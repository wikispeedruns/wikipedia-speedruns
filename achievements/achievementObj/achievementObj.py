def placeholderFun():
    return False

class achievement():
    
    def __init__(self, 
                 name,
                 description,
                 runEval=placeholderFun,
                 imgLink="/static/assets/achievementIcons/meta.png",
                 runSpecific=True,
                 secret=False,
                 userEval=placeholderFun
                 ):
        self.name = name
        self.description = description
        self.runEval = runEval
        self.imgLink = imgLink
        self.runSpecific = runSpecific
        self.secret = secret
        self.userEval = userEval
        
        
    def toString(self):
        
        return self.name + ": " + self.description
    
    
    def checkRun(self, run):
        
        if not self.runSpecific:
            return False
        
        return self.runEval(run)
    
    
    def checkUser(self, username):
        
        if self.runSpecific:
            return False
        
        return self.userEval(username)
    