import socket

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 65432  # The port used by the server


def main():
    print("dttt server: hello!")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()

        while True:
            conn, addr = s.accept()

            with conn:
                print("Connected by", addr)
                while True:
                    data = conn.recv(1024)
                    print("data:", data)
                    if not data:
                        break
                    conn.sendall(data)
