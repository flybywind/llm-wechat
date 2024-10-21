class AK_SK:
    def __init__(self, file_name:str):
        with open(file_name, 'r') as f:
            line = f.readline().strip()
            seg = line.split(',')
            self.ak = seg[0]
            self.sk = seg[1]
    
    def get_ak(self):
        return self.ak
    
    def get_sk(self):
        return self.sk