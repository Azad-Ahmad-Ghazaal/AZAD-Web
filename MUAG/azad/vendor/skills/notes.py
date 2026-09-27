import json
import os


class Notes:

    def __init__(self):

        self.file = "data/notes.json"


        if not os.path.exists(self.file):

            with open(self.file, "w") as f:
                json.dump([], f)



    def save(self, text):

        with open(self.file, "r") as f:
            notes = json.load(f)


        notes.append(text)


        with open(self.file, "w") as f:
            json.dump(notes, f, indent=4)


        return "Note saved successfully."



    def read(self):

        with open(self.file, "r") as f:
            notes = json.load(f)


        if len(notes) == 0:
            return "No notes found."


        return notes