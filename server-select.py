import json, os, select, socket
from collections import deque

HOST = "0.0.0.0"
PORT = 5000
STORAGE_DIR = "server_files"

def packet_bytes(packet):
    return bytearray((json.dumps(packet) + "\n").encode())

def list_files():
    return sorted(
        name for name in os.listdir(STORAGE_DIR) if os.path.isfile(os.path.join(STORAGE_DIR, name))
    )

def queue_file(client, path, name):
    data = open(path, "rb").read()
    client["out"].append(packet_bytes({"type": "file", "filename": name, "size": len(data)}))
    client["out"].append(bytearray(data))

def handle_packet(client, packet, clients):
    kind = packet["type"]

    if kind == "message":
        msg = packet_bytes({"type": "message", "from": client["label"], "text": packet["text"]})
        for other in clients.values():
            other["out"].append(bytearray(msg))

    elif kind == "list":
        client["out"].append(packet_bytes({"type": "list", "files": list_files()}))

    elif kind == "upload":
        name = os.path.basename(packet["filename"])
        client["upload_name"] = name
        client["upload_left"] = packet["size"]
        client["upload_file"] = open(os.path.join(STORAGE_DIR, name), "wb")

    elif kind == "download":
        name = os.path.basename(packet["filename"])
        path = os.path.join(STORAGE_DIR, name)
        if os.path.exists(path):
            queue_file(client, path, name)
        else:
            client["out"].append(packet_bytes({"type": "error", "text": f"File not found: {name}"}))

def process_input(client, clients):
    while True:
        if client["upload_file"]:
            if not client["in"]:
                return
            take = min(len(client["in"]), client["upload_left"])
            client["upload_file"].write(client["in"][:take])
            del client["in"][:take]
            client["upload_left"] -= take
            if client["upload_left"] == 0:
                client["upload_file"].close()
                client["upload_file"] = None
                client["out"].append(
                    packet_bytes({"type": "info", "text": f"Upload complete: {client['upload_name']}"})
                )
            continue

        newline = client["in"].find(b"\n")
        if newline == -1:
            return

        packet = json.loads(client["in"][:newline])
        del client["in"][: newline + 1]
        handle_packet(client, packet, clients)

def flush_output(client):
    if not client["out"]:
        return
    sent = client["sock"].send(client["out"][0])
    del client["out"][0][:sent]
    if not client["out"][0]:
        client["out"].popleft()

def close_client(clients, sock):
    client = clients.pop(sock, None)
    if client:
        if client["upload_file"]:
            client["upload_file"].close()
        sock.close()
        print("Client disconnected:", client["label"])

def main():
    os.makedirs(STORAGE_DIR, exist_ok=True)
    server = socket.socket()
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen()
    server.setblocking(False)
    clients = {}
    print(f"Select server running on {HOST}:{PORT}")

    while True:
        reads = [server, *clients]
        writes = [sock for sock, client in clients.items() if client["out"]]
        readable, writable, _ = select.select(reads, writes, [], 0.5)

        if server in readable:
            conn, addr = server.accept()
            conn.setblocking(False)
            clients[conn] = {
                "sock": conn,
                "label": f"{addr[0]}:{addr[1]}",
                "in": bytearray(),
                "out": deque(),
                "upload_file": None,
                "upload_left": 0,
                "upload_name": "",
            }
            print("Client connected:", clients[conn]["label"])
            readable.remove(server)

        for sock in readable:
            data = sock.recv(4096)
            if not data:
                close_client(clients, sock)
                continue
            clients[sock]["in"].extend(data)
            process_input(clients[sock], clients)

        for sock in writable:
            flush_output(clients[sock])

if __name__ == "__main__":
    main()
