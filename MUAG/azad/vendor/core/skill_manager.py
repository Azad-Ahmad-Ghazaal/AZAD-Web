class SkillManager:


    def __init__(self):

        self.skills = {}



    def register(self, name, skill):

        self.skills[name] = skill



    def get_skill(self, name):

        return self.skills.get(name)