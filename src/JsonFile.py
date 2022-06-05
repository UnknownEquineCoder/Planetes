import os


class JsonFile:
    """
    Wrapper class for working with json files.

    This serves as a store for the API. (2nd type of database)
    """
    def __init__(self, filename: str, data: str = ""):
        self.filename = filename
        self.data = data
        self.create_file()

    def create_file(self):
        if not os.path.exists(self.filename):
            with open(self.filename, "w+") as f:
                f.write("")

    def save(self):
        with open(self.filename, "w") as f:
            f.write(self.data)

    def write(self, data: dict):
        self.data = f"{data}\n"
        self.save()

    def __str__(self):
        return self.data
