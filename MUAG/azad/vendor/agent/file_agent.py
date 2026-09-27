from tools.read_file import ReadFileTool
from tools.write_file import WriteFileTool
from tools.safe_editor import SafeEditor


class FileAgent:

    def __init__(self):

        self.reader = ReadFileTool()

        self.writer = WriteFileTool()

        self.editor = SafeEditor()

    def handle(self, message):

        message = message.strip()

        # Read
        if message.lower().startswith("read "):

            return self.reader.read(
                message[5:].strip()
            )

        # Write
        if message.lower().startswith("write "):

            try:

                data = message[6:]

                filepath, content = data.split("|", 1)

                return self.writer.write(
                    filepath.strip(),
                    content.strip()
                )

            except:

                return "write data/test.txt | Hello"

        # Replace
        if message.lower().startswith("replace "):

            try:

                data = message[8:]

                filepath, old_text, new_text = data.split("|", 2)

                return self.editor.replace_text(
                    filepath.strip(),
                    old_text.strip(),
                    new_text.strip()
                )

            except:

                return "replace file | old | new"

        return None