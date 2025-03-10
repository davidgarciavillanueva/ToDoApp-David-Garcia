class Todo:
    def __init__(self, code_id, title:str, description:str):
        self.code_id:int  = code_id
        self.title:str = title
        self.description:str  = description
        self.completed = False
        self.tags:list[str]= []


def mark_completed(self):
    self.completed = True