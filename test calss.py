class Enfant():
    def __init__(self,name):
        self.name = name
        self.count =0
    
    def donne_nom(self):
        self.count +=1
        if self.count>3:
            return "J'en ai marre de répéter"
        else:
            return self.name
        
    def crie(self,text):
        
        print(text.upper())
        
    
    
arthur = Enfant('Arthur')
print(arthur.donne_nom())
arthur.crie('papa est méchant')
print(arthur.donne_nom())
print(arthur.donne_nom())
print(arthur.donne_nom())