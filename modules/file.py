
class File:
    def __init__(self, path:str) -> None:
        self.path = path
        self.load()
    
    def load(self) -> None:
        with open(self.path, 'r', errors="ignore") as f:
            self.file = f.read()

    def get_lines(self, refresh:bool=False):
        if refresh:
            self.load()
        return self.file.splitlines()
    
    def get_content(self, refresh:bool=False):
        if refresh:
            self.load()
        return self.file