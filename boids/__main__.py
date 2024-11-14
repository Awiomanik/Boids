from .main import main
from .Utils.save2gif import save2gif
from .Utils.display import display

if __name__ == "__main__": 
    while (temp := main()):
        if temp == "display": display()
        elif temp == "save2gif": save2gif()
