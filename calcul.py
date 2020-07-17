def add(a,b):
    return a+b

def show  ():
    filecarte='map.html'
    filepath = filecarte
    m.save(filepath)
    webbrowser.open( filepath)
    return None

if __name__=="__main__":
    a='marc'
    b='Antoine'
    print(add(a,b))