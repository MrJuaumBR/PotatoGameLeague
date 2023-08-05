from SETTINGS import *

db = dataManager()

def option1():
    name = str(input('Table name> '))
    db.delete_table(name)

options = {
    "1": option1, # Break
    "x": "break",
    "X": "break",
    "exit": "break"
}

while True:
    print("""
    \nAções:
          Escolha uma opção:
          1- Deletar Table
          x/X/exit = Sair
          ==================
    """)
    x = str(input('> '))
    y = options[x]
    if callable(y):
        y()
    else:
        if type(y) == str and y == "break":
            break