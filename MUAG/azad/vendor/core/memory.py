import json
import os


class Memory:

    def __init__(self):

        self.file = "data/memory.json"

        directory = os.path.dirname(
            self.file
        )

        if directory:
            os.makedirs(
                directory,
                exist_ok=True
            )

        if not os.path.exists(
            self.file
        ):

            with open(
                self.file,
                "w",
                encoding="utf-8"
            ) as f:

                json.dump(
                    {},
                    f,
                    indent=4
                )

    # =================================
    # LOAD MEMORY
    # =================================

    def _load(self):

        try:

            with open(
                self.file,
                "r",
                encoding="utf-8"
            ) as f:

                return json.load(f)

        except (
            json.JSONDecodeError,
            FileNotFoundError
        ):

            return {}

    # =================================
    # SAVE MEMORY
    # =================================

    def save(
        self,
        key,
        value
    ):

        data = self._load()

        data[key] = value

        with open(
            self.file,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                data,
                f,
                indent=4,
                ensure_ascii=False
            )

        return True

    # =================================
    # REMEMBER
    # =================================

    def remember(
        self,
        key
    ):

        data = self._load()

        return data.get(
            key,
            "I don't remember this."
        )