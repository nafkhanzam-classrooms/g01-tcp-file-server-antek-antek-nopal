import json, os, socket

HOST = "0.0.0.0"
PORT = 5000
STORAGE_DIR = "server_files"

def send_packet(sock, packet):
    sock.sendall((json.dumps(packet) + "\n").encode())

def list_files():
    return sorted(
        name for name in os.listdir(STORAGE_DIR) if os.path.isfile(os.path.join(STORAGE_DIR, name))
    )

def handle_client(conn, addr):
    label = f"{addr[0]}:{addr[1]}"
    reader = conn.makefile("rb")
    print("Client connected:", label)

    while True:
        raw = reader.readline()
        if not raw:
            break

        packet = json.loads(raw)
        kind = packet["type"]

        if kind == "message":
            send_packet(conn, {"type": "message", "from": label, "text": packet["text"]})

        elif kind == "list":
            send_packet(conn, {"type": "list", "files": list_files()})

        elif kind == "upload":
            name = os.path.basename(packet["filename"])
            size = packet["size"]
            with open(os.path.join(STORAGE_DIR, name), "wb") as file:
                file.write(reader.read(size))
            send_packet(conn, {"type": "info", "text": f"Upload complete: {name}"})

        elif kind == "download":
            name = os.path.basename(packet["filename"])
            path = os.path.join(STORAGE_DIR, name)
            if os.path.exists(path):
                data = open(path, "rb").read()
                send_packet(conn, {"type": "file", "filename": name, "size": len(data)})
                conn.sendall(data)
            else:
                send_packet(conn, {"type": "error", "text": f"File not found: {name}"})

    conn.close()
    print("Client disconnected:", label)

def main():
    os.makedirs(STORAGE_DIR, exist_ok=True)
    server = socket.socket()
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen()
    print(f"Synchronous server running on {HOST}:{PORT}")

    while True:
        handle_client(*server.accept())

if __name__ == "__main__":
    main()
