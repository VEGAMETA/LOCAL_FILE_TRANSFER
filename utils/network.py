import socket
import typing
import pathlib
import utils.config
import gui.popup_files_recieved
import gui.popup_duplicate_handler


class ClientServer:
    def __init__(self):
        self.server: typing.Optional[socket.socket] = None
        self.PORT = utils.config.PORT
        self.downloads_folder = utils.config.downloads_folder

    async def send_files(self, ip, selected_files):
        if selected_files and ip:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.settimeout(3)
            client.connect((ip, self.PORT))

            client.send(str(len(selected_files)).encode("utf-8"))

            for file in selected_files:
                client.send(file.name.encode("utf-8"))
                with open(file, "rb") as f:
                    file_data = f.read(1024)
                    while file_data:
                        client.send(file_data)
                        file_data = f.read(1024)

            client.close()

    async def open_connection(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(("0.0.0.0", self.PORT))
        self.server.listen(5)

        while True:
            try:
                client_socket, _ = self.server.accept()
                files_amount = client_socket.recv(1024).decode("utf-8")
                filenames = []
                for _ in range(int(files_amount)):
                    filename = client_socket.recv(1024).decode("utf-8")
                    filenames.append(filename)
                    self.handle_file_transfer(client_socket, filename)
                gui.popup_files_recieved.PopupFileRecieved(filename)
            except (KeyboardInterrupt, OSError) as e:
                break

    def handle_file_transfer(self, client_socket, filename):
        try:
            data = client_socket.recv(1024)
            if not data:
                return

            filename = pathlib.Path(self.downloads_folder + filename)
            if pathlib.Path.exists(filename):
                filename = gui.popup_duplicate_handler.PopupFileCollision(filename)

            with open(filename, "wb") as file:
                while data:
                    file.write(data)
                    data = client_socket.recv(1024)

        except Exception as e:
            print(f"Error handling file transfer: {str(e)}")

    def close_connection(self):
        if self.server:
            self.server.close()
            self.server = None
