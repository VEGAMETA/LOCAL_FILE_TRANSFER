import pathlib
import asyncio
import gui.popup_ip
import threading
import PySimpleGUI as sg
import utils.config as config
import utils.network as network

sg.theme(config.theme)


class MainWindow(sg.Window):
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
        super().__init__(
            "File transfer", layout, return_keyboard_events=True, finalize=True
        )

        self["Send"].bind("<Return>", "_SUBMIT_")
        self.client_server = network.ClientServer()
        self.server_thread = None
        self.main_loop()

    def main_loop(self):
        while True:
            event, values = self.read()

            if event == sg.WIN_CLOSED:
                self.shutdown()

            elif event == "Add file":
                self.add_file()

            elif event == "Del file":
                self.del_file(values.get("files"))

            elif event == "Add ip":
                gui.popup_ip.PopupIP(self.available_ips, self["ips"])

            elif event == "Del ip":
                self.del_ip(values.get("ips"))

            elif event == "Send":
                self.send_files(values.get("ips"))

            elif event == "Receive":
                self.recieve_files(values.get("Receive"))

    def shutdown(self):
        self.server_thread = None
        self.client_server.close_connection()
        self.close()
        exit(0)

    def add_file(self):
        filename = pathlib.Path(
            sg.popup_get_file("Will not see this message", no_window=True)
        )
        if filename in self.selected_files:
            sg.popup_error("Filename in the list already")
            return
        self.selected_files.append(filename)
        self["files"].update(values=[file.name for file in self.selected_files])

    def del_file(self, files):
        if not files:
            return
        for file in self.selected_files:
            if file.name == files[0]:
                self.selected_files.remove(file)
                self["files"].update(values=[file.name for file in self.selected_files])
                return

    def del_ip(self, names):
        if not names:
            return
        for ip in self.available_ips:
            if names[0] == ip.get("name"):
                self.available_ips.remove(ip)
                self["ips"].update(
                    values=[host.get("name") for host in self.available_ips]
                )
                with open("ips.txt", "w") as f:
                    for host in self.available_ips:
                        f.write(f"{host.get('ip')} {host.get('name')}\n")
                break

    def send_files(self, names):
        if not names:
            sg.popup_error("Ip hasn't been chosen")
            return
        elif not self.selected_files:
            sg.popup_error("Files hasn't been chosen")
            return
        else:
            for host in self.available_ips:
                if names[0] == host.get("name"):
                    ip = host.get("ip")
                    break
            else:
                return
        try:
            asyncio.run(self.client_server.send_files(ip, self.selected_files))
            sg.popup("File(s) sent")
        except Exception as e:
            sg.popup_error(f"Error sending files: {str(e)}")

    def recieve_files(self, recieve):
        if recieve:
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
