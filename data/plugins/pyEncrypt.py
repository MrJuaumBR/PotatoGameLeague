from random import randint
from os import path

class pyEncrypt():
    def __init__(self,autostart=True,path='/') -> None:
        self.key = ""
        self.dkey = {}
        self.rdkey = {}
        self.ver = self.version()
        self.key_file = ""
        self.path = path
        self.autostart(autostart) # Create key file if note exists
            
    def version(self):
        """Return pyEncrypt version"""
        return "0.0.1 - https://mrjuaumbr.github.io"
    
    def autostart(self,autostart:bool):
        if autostart:
            self.start()

    def start(self):
        if not self.check_key():
            print("pyEncrypt > (create key file or key corrupted generating other.)")
            self.create_keyfile()
            self.rdkey = self.get_dict()
            self.write_keyfile()
        else:
            print("pyEncrypt > Key exists!")
            self.rdkey = {"alphabet":self.read_keyfile()}

    def string_to_list(self,value:str) -> list:
        """Converts a string to list by character"""
        a = []
        for ltr in value:
            a.append(ltr)
        return a
    
    def list_to_string(self,value:list) -> str:
        """Converts a list to string by item"""
        a = ""
        for ltr in value:
            a+= ltr
        return a

    def random_gen(self,list_key:list,dict_type:str)-> str:
        """Check if this already in key"""
        r = self.dkey[dict_type][randint(0,len(self.dkey[dict_type])-1)]
        if r in list_key:
            r = self.random_gen(list_key,dict_type)
            return r
        else:
            return r

    def create_keydict(self):
        k = {"alphabet":[],"nalphabet":[]}
        alphabet = """ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890!@#$%¨&*(-)+=:'`{,<}.>^~;/?\|§" ][_"""
        alphabet = self.string_to_list(alphabet)
        k['alphabet'] = alphabet
        self.dkey = k

    def check_key(self)->bool:
        """Check if key already exists"""
        if path.exists(f'{self.path}/key.key'):
            if open(f'{self.path}/key.key','rb').read() in [""," ", None, self.ver]:
                return False
            else:
                return True
        else:
            return False

    def create_keyfile(self):
        """Create the key.key file"""
        if self.key in ["",None,"None"]:
            with open(f'{self.path}/key.key','w+') as f:
                f.write("Key "+self.version())
            self.key_file = str(open(f'{self.path}/key.key','rb').read())

    def validate_x(self,x,y,lk):
        if x.isalpha():
            if y.isalpha():
                return y
            else:
                y2 = self.random_gen(lk,'alphabet')
                return self.validate_x(x,y2,lk)
        else:
            if y.isalpha():
                y2 = self.random_gen(lk,'alphabet')
                return self.validate_x(x,y2,lk)
            else:
                return y

    def get_dict(self) -> dict:
        """Gen the key dictionaire"""
        try: # Check if alphabet exists
            self.dkey['alphabet'].count()
        except:
            self.create_keydict()

        alpha = {}
        already = []
        size_of = 0
        for ltr in self.dkey['alphabet']:
            if not (ltr in alpha):
                if size_of >= len(self.dkey['alphabet']): # If passed from len stop
                    break
                x = self.random_gen(already,'alphabet')
                if not (x in alpha):
                    x = self.validate_x(ltr,x,already)
                    size_of+=1
                    alpha[x] = ltr
                    alpha[ltr] = x
                    already.append(x)
                    already.append(ltr)

        return {'alphabet':alpha}
    
    def write_keyfile(self):
        key_path = f'{self.path}/key.key'
        text = []
        for key in self.rdkey['alphabet'].keys():
            if not key in text:
                text.append(str(key))
                text.append(self.rdkey['alphabet'][str(key)])
        text = self.list_to_string(text)
        with open(key_path,'w+') as f:
            f.write(text)
    
    def read_keyfile(self)->dict:
        key_path = f'{self.path}/key.key'
        v = str(open(key_path,'r+').read())
        key_ = {}
        for i,ltr in enumerate(v):
            if not i+1 > len(v)-1:
                x = i+1
            else:
                x = i
            if not (v[x] in key_.keys()) and not (ltr in key_.keys()):
                key_[ltr] = v[x]
                key_[v[x]] = ltr
            else:
                pass
        return key_

    def encrypt(self,text:str or int) -> str:
        """Encrypt your text"""
        text = str(text)
        new_text = ""
        for ltr in text:
            if ltr.isalpha() and ltr.islower():
                ltr = ltr.upper()
                ltr = self.rdkey['alphabet'][str(ltr)]
                new_text += ltr
            elif ltr.isalpha() and ltr.isupper():
                ltr = ltr.upper()
                ltr = self.rdkey['alphabet'][str(ltr)]
                new_text += ltr.lower()
            else:
                ltr = self.rdkey['alphabet'][str(ltr)]
                new_text += ltr
        return new_text
    
    def deencrypt(self,text:str or int) -> str:    
        text = str(text)
        new_text = ""
        for ltr in text:
            if ltr.isalpha():
                l = ltr.upper()
            else:
                l = ltr

            if ltr.islower():
                l = self.rdkey['alphabet'][l]
                new_text += l.upper()
            elif ltr.isupper():
                l = self.rdkey['alphabet'][l]
                new_text += l.lower()
            else:
                l = self.rdkey['alphabet'][ltr]
                new_text += l

        return new_text
    
if __name__ == "__main__":
    pye = pyEncrypt(True,'./data/')
    import json
    """with open('./data/values.json','rb') as f:
        j = json.loads(f.read())
        for key in j.keys():
            print(key,pye.encrypt(j[key]))"""