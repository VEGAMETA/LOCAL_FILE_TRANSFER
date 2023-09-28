import PySimpleGUI as sg
import utils.explorer


class PopupFileRecieved(sg.Window):
    def __init__(self, filename):
        self.filename = filename

        layout = [
            [sg.Text("File Recieved")],
            [sg.Button("OK", key="-OK-")],
            [sg.Button("Open in explorer", key="-OPEN-")],
        ]

        super().__init__("Operation completed", layout=layout, finalize=True)

        self["-OK-"].bind("<Return>", "OK")
        self.main_loop()
        self.close()

    def main_loop(self):
        while True:
            event, _ = self.read()
            if event in (sg.WINDOW_CLOSED, "-OK-", "\r"):
                break
            elif event == "-OPEN-":
                utils.explorer.open_explorer(self.filename.parent)
