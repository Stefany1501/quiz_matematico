import socket
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def discover_server():
    """Descobre o servidor na rede local."""
    UDP_PORT = 9000
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s.settimeout(5)

    s.sendto("DISCOVER_SERVER".encode("utf-8"), ("255.255.255.255", UDP_PORT))
    try:
        data, addr = s.recvfrom(1024)
        response = data.decode("utf-8").strip()
        if response.startswith("SERVER_HERE"):
            parts = response.split("|")
            return parts[1], int(parts[2])
    except Exception as e:
        logging.error(f"Erro ao descobrir servidor: {e}")
    finally:
        s.close()
    return None, None

def play_game():
    """Conecta ao servidor e inicia o jogo."""
    server_ip, server_port = discover_server()
    if not server_ip:
        print("Servidor não encontrado.")
        return

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((server_ip, server_port))
        print("Conectado ao servidor.")

        name_prompt = client.recv(1024).decode("utf-8")
        print(name_prompt)
        player_name = input("Seu nome: ")
        client.send(player_name.encode("utf-8"))

        mode_prompt = client.recv(1024).decode("utf-8")
        print(mode_prompt)
        choice = input("Digite 1 para Single Player ou 2 para Multiplayer: ")
        client.send(choice.encode("utf-8"))

        if choice == "2":
            # Modo Multiplayer
            while True:
                data = client.recv(1024).decode("utf-8")
                if not data:
                    break

                print(data)

                if data.startswith("Sua vez!") or data.startswith("Resolva:"):
                    answer = input("Sua resposta: ")
                    client.send(answer.encode("utf-8"))
                elif data.startswith("Fim de jogo"):
                    print("Fim do jogo multiplayer.")
                    break
                elif data.startswith("Aguardando outro jogador..."):
                    print("Espere que logo você enfrentará um oponente.")

        else:
            # Modo Single Player
            while True:
                data = client.recv(1024).decode("utf-8")
                if not data:
                    break
                print(data)
                if data.startswith("Escolha a dificuldade"):
                    difficulty = input("Digite a dificuldade (1-4): ")
                    client.send(difficulty.encode("utf-8"))
                elif data.startswith("Resolva:"):
                    answer = input("Sua resposta: ")
                    client.send(answer.encode("utf-8"))
                elif data.startswith("Fim de jogo"):
                    play_again = input("Deseja jogar novamente? (sim/nao): ")
                    client.send(play_again.encode("utf-8"))
                    if play_again.lower() == "nao":
                        break

    except Exception as e:
        logging.error(f"Erro durante o jogo: {e}")
    finally:
        client.close()
        print("Conexão encerrada.")

if __name__ == '__main__':
    play_game()