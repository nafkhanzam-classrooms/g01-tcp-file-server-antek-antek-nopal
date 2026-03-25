import json
import os
import socket
import threading

HOST = "0.0.0.0"
PORT = 5000
STORAGE_DIR = "server_files"

clients = []
clients_lock = threading.Lock()

def send_packet(client, packet):
    data = (json.dumps(packet) + "\n").encode()
    with client["lock"]:
        client["sock"].sendall(data)


def send_file(client, path, name):
    data = open(path, "rb").read()
    with client["lock"]:
        client["sock"].sendall((json.dumps({"type": "file", "filename": name, "size": len(data)}) + "\n").encode())
        client["sock"].sendall(data)


def list_files():
    return sorted(
        name for name in os.listdir(STORAGE_DIR) if os.path.isfile(os.path.join(STORAGE_DIR, name))
    )

def broadcast(packet):
    with clients_lock:
        current = list(clients)
    for client in current:
        send_packet(client, packet)

def handle_client(conn, addr):
    client = {
        "sock": conn,
        "addr": addr,
        "label": f"{addr[0]}:{addr[1]}",
        "reader": conn.makefile("rb"),
        "lock": threading.Lock(),
    }

    with clients_lock:
        clients.append(client)

    print("Client connected:", client["label"])

    while True:
        raw = client["reader"].readline()
        if not raw:
            break

        packet = json.loads(raw)
        kind = packet["type"]

        if kind == "message":
            broadcast({"type": "message", "from": client["label"], "text": packet["text"]})

        elif kind == "list":
            send_packet(client, {"type": "list", "files": list_files()})

        elif kind == "upload":
            name = os.path.basename(packet["filename"])
            size = packet["size"]
            with open(os.path.join(STORAGE_DIR, name), "wb") as file:
                file.write(client["reader"].read(size))
            send_packet(client, {"type": "info", "text": f"Upload complete: {name}"})

        elif kind == "download":
            name = os.path.basename(packet["filename"])
            path = os.path.join(STORAGE_DIR, name)
            if os.path.exists(path):
                send_file(client, path, name)
            else:
                send_packet(client, {"type": "error", "text": f"File not found: {name}"})

    with clients_lock:
        if client in clients:
            clients.remove(client)
    conn.close()
    print("Client disconnected:", client["label"])

def main():
    os.makedirs(STORAGE_DIR, exist_ok=True)
    server = socket.socket()
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen()
    print(f"Threaded server running on {HOST}:{PORT}")

    while True:
        threading.Thread(target=handle_client, args=server.accept(), daemon=True).start()


if __name__ == "__main__":
    main()
