import os


class ProjectReader:

    def __init__(self, root):

        self.root = root


    def scan(self):

        project = []

        for folder, _, files in os.walk(self.root):

            for file in files:

                project.append(
                    os.path.join(folder, file)
                )

        return project
    