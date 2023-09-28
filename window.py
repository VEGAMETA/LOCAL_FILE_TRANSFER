import re
import time
import asyncio
import network
import pathlib
import threading
import PySimpleGUI as sg


class FileTransfer(sg.Window):
    def __init__(self):
        self.selected_files = []
        self.available_ips = self.get_ips()

        layout = [
            [
                [
                    sg.Text("Files", size=(32, 1)),
                    sg.Text("PC ip", size=(20, 1)),
                    sg.Checkbox("Get files", change_submits=True, key="Receive"),
                ],
                [
                    sg.Listbox(
                        values=self.selected_files,
                        size=(36, 6),
                        key="files",
                        no_scrollbar=True,
                    ),
                    sg.Listbox(
                        values=[file.get("name") for file in self.available_ips],
                        size=(36, 6),
                        key="ips",
                        no_scrollbar=True,
                    ),
                ],
                [
                    sg.Button("Add file", size=(14, 1)),
                    sg.Button("Del file", size=(14, 1)),
                    sg.Button("Add ip", size=(15, 1)),
                    sg.Button("Del ip", size=(14, 1)),
                ],
                sg.Button("Send", size=(64, 3)),
            ],
        ]
        super().__init__("File transfer", layout, finalize=True)
        self.client_server = network.ClientServer()
        self.server_thread = None
        self.main_loop()

    def main_loop(self):
        while True:
            event, values = self.read()

            if event == sg.WIN_CLOSED or event == "Cancel":
                self.server_thread = None
                self.client_server.close_connection()
                self.close()
                exit(0)

            elif event == "Add file":
                filename = pathlib.Path(
                    sg.popup_get_file("Will not see this message", no_window=True)
                )
                if filename in self.selected_files:
                    sg.popup_error("Filename in the list already")
                    continue
                self.selected_files.append(filename)
                self["files"].update(values=[file.name for file in self.selected_files])

            elif event == "Del file":
                for file in self.selected_files:
                    if file.name == values.get("files")[0]:
                        self.selected_files.remove(file)
                        break
                self["files"].update(values=[file.name for file in self.selected_files])

            elif event == "Add ip":
                layout = [
                    [sg.Text("Name:\t\t"), sg.Input(key="-NAME-")],
                    [sg.Text("IP Address:\t"), sg.Input(key="-IP-")],
                    [sg.Button("Submit")],
                ]
                window = sg.Window("Enter Name and IP", layout)

                while True:
                    event, values = window.read()
                    if event == sg.WINDOW_CLOSED:
                        break
                    elif event == "Submit":
                        name = values["-NAME-"]
                        ip = values["-IP-"]
                        pattern = r"^(\d{1,3}\.){3}\d{1,3}$"
                        if not name:
                            sg.popup_error("Name hasn't been entered")
                        if re.match(pattern, ip) is not None:
                            self.available_ips.append({"name": name, "ip": ip})
                            window.close()
                            self["ips"].update(
                                values=[host.get("name") for host in self.available_ips]
                            )
                            with open("ips.txt", "w") as f:
                                for host in self.available_ips:
                                    f.write(f"{host.get('ip')} {host.get('name')}\n")
                            break
                        else:
                            sg.popup_error("Invalid IP")

            elif event == "Del ip":
                for ip in self.available_ips:
                    if ip.get("name") == values.get("ips")[0]:
                        self.available_ips.remove(ip)
                        self["ips"].update(
                            values=[host.get("name") for host in self.available_ips]
                        )
                        with open("ips.txt", "w") as f:
                            for host in self.available_ips:
                                f.write(f"{host.get('ip')} {host.get('name')}\n")
                        break

            elif event == "Send":
                if not values.get("ips"):
                    sg.popup_error("Ip hasn't been chosen")
                    continue
                elif not self.selected_files:
                    sg.popup_error("Files hasn't been chosen")
                    continue
                else:
                    for host in self.available_ips:
                        if values.get("ips")[0] == host.get("name"):
                            ip = host.get("ip")
                            break
                    else:
                        continue
                try:
                    asyncio.run(self.client_server.send_files(ip, self.selected_files))
                except Exception as e:
                    sg.popup_error(f"Error sending files: {str(e)}")

            elif event == "Receive":
                if values.get("Receive"):
                    self.server_thread = threading.Thread(
                        target=asyncio.run, args=(self.client_server.open_connection(),)
                    )
                    self.server_thread.start()
                else:
                    self.server_thread = None
                    self.client_server.close_connection()

    def get_ips(self):
        with open("ips.txt", "r") as f:
            ips = [
                {"ip": host[0], "name": host[1]}
                for host in [host.split(" ", 1) for host in f.read().splitlines()]
            ]
            return ips
