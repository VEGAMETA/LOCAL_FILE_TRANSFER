import socket
import subprocess
import typing


class ClientServer:
    def __init__(self):
        self.server: typing.Optional[socket.socket] = None
        self.PORT = 23091
        self.downloads_folder = "D:/Downloads/"

    @staticmethod
    def get_ips():
        local_ips = []

        try:
            arp_result = subprocess.check_output(["arp", "-a"], universal_newlines=True)
            lines = arp_result.split("\n")
            for line in lines:
                parts = line.split()
                if (
                    len(parts) >= 2
                    and parts[0].startswith("192")
                    and parts[0] not in ("192.168.1.255", "192.168.1.1")
                ):
                    ip_address = parts[0]
                    local_ips.append(
                        {"name": socket.gethostbyaddr(ip_address)[0], "ip": ip_address}
                    )
        except subprocess.CalledProcessError:
            pass

        return list(local_ips)

    async def send_files(self, ip, selected_files):
        if selected_files and ip:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.settimeout(3)
            client.connect((ip, self.PORT))

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
        print("Server started")
        self.server.listen(5)

        while True:
            try:
                client_socket, _ = self.server.accept()
                filename = client_socket.recv(1024).decode("utf-8")
                self.handle_file_transfer(client_socket, filename)
            except (KeyboardInterrupt, OSError) as e:
                print(f"Error handling file transfer: {str(e)}")
                break

    def handle_file_transfer(self, client_socket, filename):
        try:
            data = client_socket.recv(1024)
            if not data:
                return

            filename = self.downloads_folder + filename

            with open(filename, "wb") as file:
                while data:
                    file.write(data)
                    data = client_socket.recv(1024)

        except Exception as e:
            print(f"Error handling file transfer: {str(e)}")

    async def close_connection(self):
        if self.server:
            self.server.close()
            self.server = None
            print("Server closed")
