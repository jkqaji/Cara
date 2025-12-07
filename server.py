import socket
import threading
import os

# Porta automática no Render
PORT = int(os.environ.get("PORT", 5050))
HOST = "0.0.0.0"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

clientes = {}
admins = set()
ADM_SENHA = "meumano"  # senha secreta

def enviar_para_todos(msg):
    for c in list(clientes.keys()):
        try:
            c.send(msg.encode())
        except:
            pass

def tratar_comandos(conn, nome, msg):
    # LOGIN ADMIN
    if msg.startswith("/admin "):
        senha = msg.split(" ", 1)[1]
        if senha == ADM_SENHA:
            admins.add(conn)
            conn.send("✔ Você agora é ADMIN!".encode())
        else:
            conn.send("❌ Senha errada!".encode())
        return True

    # Se não for admin, não pode usar comandos
    if conn not in admins:
        return False

    # BROADCAST
    if msg.startswith("/broadcast "):
        texto = msg.split(" ", 1)[1]
        enviar_para_todos(f"[ADM] {texto}")
        return True

    # KICK
    if msg.startswith("/kick "):
        alvo = msg.split(" ", 1)[1]
        for c, n in clientes.items():
            if n == alvo:
                try:
                    c.send("❌ Você foi expulso pelo ADM!".encode())
                    c.close()
                except:
                    pass
                enviar_para_todos(f"[ADM] {alvo} foi expulso.")
                return True
        conn.send("Jogador não encontrado.".encode())
        return True

    # TELEPORTE
    if msg.startswith("/tp "):
        try:
            x, y = msg.split(" ")[1:]
            enviar_para_todos(f"TP {nome} {x} {y}")
            return True
        except:
            conn.send("Formato correto: /tp X Y".encode())
            return True

    return False


def handle(conn):
    nome = conn.recv(1024).decode()
    clientes[conn] = nome
    enviar_para_todos(f"{nome} entrou no jogo.")

    while True:
        try:
            msg = conn.recv(1024).decode()
            if not msg:
                break

            if tratar_comandos(conn, nome, msg):
                continue

            enviar_para_todos(f"{nome}: {msg}")

        except:
            break

    enviar_para_todos(f"{nome} saiu do jogo.")
    del clientes[conn]
    conn.close()


print(f"Servidor iniciado na porta {PORT}...")
while True:
    conn, addr = server.accept()
    threading.Thread(target=handle, args=(conn,)).start()