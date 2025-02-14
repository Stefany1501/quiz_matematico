import socket
import threading
import random
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Variáveis globais
waiting_players = []
lock = threading.Lock()

def generate_math_problem(difficulty):
    """Gera uma conta matemática simples com base na dificuldade."""
    operations = ['+', '-', '*', '/']
    operation = random.choice(operations)
    if difficulty == "Fácil":
        num1 = random.randint(1, 10)
        num2 = random.randint(1, 10)
    elif difficulty == "Normal":
        num1 = random.randint(10, 20)
        num2 = random.randint(5, 15)
    elif difficulty == "Difícil":
        num1 = random.randint(20, 30)
        num2 = random.randint(10, 20)
    else:
        num1 = random.randint(30, 50)
        num2 = random.randint(15, 30)

    if operation == '/':
        num1 = num1 * num2
    problem = f"{num1} {operation} {num2}"
    try:
        answer = eval(problem)
    except ZeroDivisionError:
        # Se ocorrer divisão por zero, gera um novo problema
        return generate_math_problem(difficulty)
    return problem, answer

def handle_single_player(client_socket, addr, player_name):
    """Lida com uma partida individual."""
    score = 0
    mistakes = 0

    client_socket.send("Escolha a dificuldade:\n1. Fácil\n2. Normal\n3. Difícil\n4. Especialista".encode("utf-8"))
    difficulty_choice = client_socket.recv(1024).decode("utf-8").strip()

    if difficulty_choice == "1":
        difficulty = "Fácil"
    elif difficulty_choice == "2":
        difficulty = "Normal"
    elif difficulty_choice == "3":
        difficulty = "Difícil"
    else:
        difficulty = "Especialista"

    logging.info(f"Conexão estabelecida com {addr} (Modo Single Player - {difficulty})")
    client_socket.send(f"Bem-vindo(a), {player_name} ao Quiz Matemático (Modo Single Player - {difficulty})!".encode("utf-8"))

    while mistakes < 3:
        problem, answer = generate_math_problem(difficulty)
        client_socket.send(f"Resolva: {problem}".encode("utf-8"))

        try:
            response = client_socket.recv(1024).decode("utf-8").strip()
            if not response:
                break

            if float(response) == answer:
                score += 1
                client_socket.send(f"Correto! Pontuação: {score}".encode("utf-8"))
            else:
                mistakes += 1
                client_socket.send(f"Incorreto! Resposta correta: {answer}. Erros: {mistakes}/3".encode("utf-8"))
        except Exception as e:
            logging.error(f"Erro ao processar resposta de {addr}: {e}")
            break

    client_socket.send(f"Fim de jogo! Pontuação final: {score}".encode("utf-8"))

    # Quer ogar novamente?
    play_again = client_socket.recv(1024).decode("utf-8").strip().lower()

    return play_again == "sim"

def handle_multiplayer(player1, player2):
    """Lida com uma partida multiplayer."""
    p1_socket, p1_addr = player1
    p2_socket, p2_addr = player2
    p1_score = 0
    p2_score = 0
    p1_mistakes = 0
    p2_mistakes = 0

    logging.info(f"Partida multiplayer iniciada entre {player1[1]} e {player2[1]}")

    p1_socket.send("Bem-vindo ao Quiz Matemático (Modo Multiplayer)!".encode("utf-8"))
    p2_socket.send("Bem-vindo ao Quiz Matemático (Modo Multiplayer)!".encode("utf-8"))

    while p1_mistakes < 3 and p2_mistakes < 3:
        # Vez do jogador 1
        problem, answer = generate_math_problem("Normal")
        p1_socket.send(f"Sua vez! Resolva: {problem}".encode("utf-8"))
        p2_socket.send(f"Aguardando jogada do oponente...".encode("utf-8"))

        try:
            response = p1_socket.recv(1024).decode("utf-8").strip()
            if float(response) == answer:
                p1_score += 1
                p1_socket.send(f"Correto! Pontuação: {p1_score}".encode("utf-8"))
                p2_socket.send("Oponente acertou!".encode("utf-8"))
            else:
                p1_mistakes += 1
                p1_socket.send(f"Incorreto! Resposta correta: {answer}. Erros: {p1_mistakes}/3".encode("utf-8"))
                p2_socket.send("Oponente errou!".encode("utf-8"))
        except Exception as e:
            logging.error(f"Erro ao processar resposta de {p1_addr}: {e}")
            break

        # Vez do jogador 2
        problem, answer = generate_math_problem("Normal")
        p2_socket.send(f"Sua vez! Resolva: {problem}".encode("utf-8"))
        p1_socket.send(f"Aguardando jogada do oponente...".encode("utf-8"))

        try:
            response = p2_socket.recv(1024).decode("utf-8").strip()
            if float(response) == answer:
                p2_score += 1
                p2_socket.send(f"Correto! Pontuação: {p2_score}".encode("utf-8"))
                p1_socket.send("Oponente acertou!".encode("utf-8"))
            else:
                p2_mistakes += 1
                p2_socket.send(f"Incorreto! Resposta correta: {answer}. Erros: {p2_mistakes}/3".encode("utf-8"))
                p1_socket.send("Oponente errou!".encode("utf-8"))
        except Exception as e:
            logging.error(f"Erro ao processar resposta de {p2_addr}: {e}")
            break

    # Resultado final
    if p1_score > p2_score:
        p1_socket.send("Fim de jogo! Você venceu!".encode("utf-8"))
        p2_socket.send("Fim de jogo! O oponente venceu!".encode("utf-8"))
    elif p2_score > p1_score:
        p1_socket.send("Fim de jogo! O oponente venceu!".encode("utf-8"))
        p2_socket.send("Fim de jogo! Você venceu!".encode("utf-8"))
    else:
        p1_socket.send("Fim de jogo! Empate!".encode("utf-8"))
        p2_socket.send("Fim de jogo! Empate!".encode("utf-8"))

    p1_socket.close()
    p2_socket.close()
    logging.info(f"Partida multiplayer encerrada entre {player1[1]} e {player2[1]}.")

def handle_client(client_socket, addr):
    """Lida com a conexão de um cliente."""
    global waiting_players

    try:
        client_socket.send("Digite seu nome:".encode("utf-8"))
        player_name = client_socket.recv(1024).decode("utf-8").strip()

        client_socket.send("Escolha o modo de jogo:\n1. Single Player\n2. Multiplayer".encode("utf-8"))
        choice = client_socket.recv(1024).decode("utf-8").strip()

        if choice == "1":
            play_again = True
            while play_again:
                play_again = handle_single_player(client_socket, addr, player_name)
            client_socket.close()
            logging.info(f"Conexão com {addr} encerrada.")

        elif choice == "2":
            with lock:
                waiting_players.append((client_socket, addr))
                if len(waiting_players) >= 2:
                    player1 = waiting_players.pop(0)
                    player2 = waiting_players.pop(0)
                    threading.Thread(target=handle_multiplayer, args=(player1, player2)).start()
                else:
                    client_socket.send("Aguardando outro jogador...".encode("utf-8"))
        else:
            client_socket.send("Opção inválida.".encode("utf-8"))
            client_socket.close()
    except Exception as e:
        logging.error(f"Erro ao processar conexão de {addr}: {e}")
        client_socket.close()

def discovery_service(tcp_port):
    """Serviço de descoberta via UDP."""
    UDP_PORT = 9000
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.bind(("0.0.0.0", UDP_PORT))
        logging.info("Serviço de descoberta iniciado na porta UDP %s.", UDP_PORT)
        while True:
            data, addr = s.recvfrom(1024)
            if data.decode("utf-8").strip() == "DISCOVER_SERVER":
                response = f"SERVER_HERE|{socket.gethostbyname(socket.gethostname())}|{tcp_port}"
                s.sendto(response.encode("utf-8"), addr)
                logging.info(f"Resposta de descoberta enviada para {addr}: {response}")
    except Exception as e:
        logging.error(f"Erro no serviço de descoberta: {e}")
    finally:
        s.close()

def run_server():
    """Inicia o servidor."""
    tcp_port = 8000
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", tcp_port))
    server.listen(5)
    logging.info(f"Servidor ouvindo em 0.0.0.0:{tcp_port}")

    discovery_thread = threading.Thread(target=discovery_service, args=(tcp_port,), daemon=True)
    discovery_thread.start()

    while True:
        client_socket, addr = server.accept()
        threading.Thread(target=handle_client, args=(client_socket, addr)).start()

if __name__ == '__main__':
    run_server()