import asyncio
import network
import pathlib
import threading
import PySimpleGUI as sg


class FileTransfer(sg.Window):
    def __init__(self):
        self.selected_files = []
        self.available_ips = []
        layout = [
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
                    values=self.available_ips,
                    size=(36, 6),
                    key="ips",
                    no_scrollbar=True,
                ),
            ],
            [
                sg.Button("Add file", size=(14, 1)),
                sg.Button("Del file", size=(14, 1)),
                sg.Button("Send", size=(32, 1)),
            ],
        ]
        super().__init__("File transfer", layout, finalize=True)
        self.client_server = network.ClientServer()
        self.server_thread = None
        asyncio.run(self.run())
        self.close()

    async def run(self):
        await asyncio.gather(self.update_ips(), self.main_loop())

    async def main_loop(self):
        while True:
            event, values = self.read()

            if event == sg.WIN_CLOSED or event == "Cancel":
                self.server_thread = None
                await self.client_server.close_connection()
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
                    await self.client_server.send_files(ip, self.selected_files)
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
                    await self.client_server.close_connection()

    async def update_ips(self):
        while True:
            try:
                self.available_ips = self.client_server.get_ips()
                values = [host.get("name") for host in self.available_ips]
                self["ips"].update(values=values)
                await asyncio.sleep(1)
            except sg.tk.TclError as e:
                print(f"Error updating ips: {str(e)}")
                break
