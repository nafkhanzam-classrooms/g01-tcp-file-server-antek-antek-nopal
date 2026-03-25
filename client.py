import json, os, socket, threading

HOST = "127.0.0.1"
PORT = 5000
DOWNLOAD_DIR = "client_downloads"

def send_packet(sock, packet):
    sock.sendall((json.dumps(packet) + "\n").encode())

def print_packet(packet):
    if packet["type"] == "message":
        print(f"[{packet['from']}] {packet['text']}")
    elif packet["type"] == "list":
        print("Files on server:")
        for name in packet["files"] or ["(empty)"]:
            print(f"- {name}")
    else:
        print(packet["text"])

def receive(sock):
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    reader = sock.makefile("rb")

    while True:
        raw = reader.readline()
        if not raw:
            break

        packet = json.loads(raw)
        if packet["type"] == "file":
            name = os.path.basename(packet["filename"])
            path = os.path.join(DOWNLOAD_DIR, name)
            with open(path, "wb") as file:
                file.write(reader.read(packet["size"]))
            print(f"Downloaded {name} -> {path}")
        else:
            print_packet(packet)

def upload(sock, path):
    if not os.path.isfile(path):
        print(f"File not found: {path}")
        return

    name = os.path.basename(path)
    data = open(path, "rb").read()
    send_packet(sock, {"type": "upload", "filename": name, "size": len(data)})
    sock.sendall(data)

def main():
    sock = socket.socket()
    sock.connect((HOST, PORT))
    print(f"Connected to {HOST}:{PORT}")
    print("Commands: /list, /upload <filename>, /download <filename>")

    threading.Thread(target=receive, args=(sock,), daemon=True).start()

    while True:
        try:
            message = input().strip()
        except EOFError:
            break

        if not message:
            continue

        if message == "/list":
            send_packet(sock, {"type": "list"})
        elif message.startswith("/upload "):
            upload(sock, message[8:].strip())
        elif message.startswith("/download "):
            send_packet(sock, {"type": "download", "filename": message[10:].strip()})
        else:
            send_packet(sock, {"type": "message", "text": message})

    sock.close()

if __name__ == "__main__":
    main()
