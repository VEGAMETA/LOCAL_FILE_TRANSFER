import re
import PySimpleGUI as sg


class PopupIP(sg.Window):
    def __init__(self, available_ips, ips):
        self.available_ips = available_ips
        self.ips = ips
        layout = [
            [sg.Text("Name:\t\t"), sg.Input(key="-NAME-")],
            [sg.Text("IP Address:\t"), sg.Input(key="-IP-")],
            [sg.Button("Submit", key="-SUBMIT-")],
        ]

        super().__init__(
            "Enter Name and IP", layout, return_keyboard_events=True, finalize=True
        )

        self["-SUBMIT-"].bind("<Return>", "submit")
        self.main_loop()
        self.close()

    def main_loop(self):
        while True:
            event, values = self.read()
            if event == sg.WINDOW_CLOSED:
                break

            elif event in ("-SUBMIT-", "\r"):
                name = values["-NAME-"]
                ip = values["-IP-"]
                pattern = r"^(\d{1,3}\.){3}\d{1,3}$"
                if not name:
                    sg.popup_error("Name hasn't been entered")
                if re.match(pattern, ip) is not None:
                    self.available_ips.append({"name": name, "ip": ip})
                    self.ips.update(
                        values=[host.get("name") for host in self.available_ips]
                    )
                    with open("ips.txt", "w") as f:
                        for host in self.available_ips:
                            f.write(f"{host.get('ip')} {host.get('name')}\n")
                    break
                else:
                    sg.popup_error("Invalid IP")
