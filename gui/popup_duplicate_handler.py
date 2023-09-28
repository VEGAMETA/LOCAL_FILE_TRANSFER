import PySimpleGUI as sg
import pathlib


class PopupFileCollision(sg.Window):
    def __init__(self, filename):
        self.filename = filename.name
        self.filename_duplicate = filename.name
        duplicate_number = 1

        while pathlib.Path.exists(filename.parent + "/" + self.filename_duplicate):
            self.filename_duplicate = f"{self.filename} ({duplicate_number})"
            duplicate_number += 1

        layout = [
            [sg.Text("Duplicate handler")],
            [
                sg.Button(
                    "Save duplicate file as {self.filename_duplicate}",
                    key="-DUPLICATE-",
                )
            ],
            [sg.Button("Rewrite file", key="-REWRITE-")],
            [sg.Button("Cancel", key="-CANCEL-")],
        ]

        super().__init__("File Collision", layout=layout, finalize=True)
        filename_final = self.main_loop()
        self.close()
        return filename.parent + "/" + filename_final

    def main_loop(self):
        while True:
            event, _ = self.read()
            if event in (sg.WINDOW_CLOSED, "-CANCEL-"):
                break
            elif event == "-DUPLICATE-":
                return self.filename_duplicate
            elif event == "-REWRITE-":
                return self.filename
