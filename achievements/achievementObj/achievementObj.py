class achievement():
    
    def __init__(self, 
                 name,
                 description,
                 evalFunction,
                 imgLink="/assets/images/a.png",
                 runSpecific=True,
                 secret=False
                 ):
        self.name = name
        self.description = description
        self.evalFunction = evalFunction
        self.imgLink = imgLink
        self.runSpecific = runSpecific
        self.secret = secret
        
        
    def toString(self):
        
        return self.name + ": " + self.description
    
    
    def checkRun(self, run):
        
        if not self.runSpecific:
            return False
        
        return self.evalFunction(run)
    
    
    def checkUser(self, username):
        
        if self.runSpecific:
            return False
        
        return self.evalFunction(username)
    