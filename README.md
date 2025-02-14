# quiz_matematico
Trabalho final da disciplina de Redes de Computadores

# 🧮 Quiz Matemático em Python
Este é um jogo desenvolvido em Python, fazendo a comunicação por redes via socket.
No quiz matemático contas simples de divisão, multiplicação, adição e subtração são geradas para que o jogador calcule mentalmente e informe o resultado. A partir disso, o sistema calcula a pontuação e, se houver, no máximo, três falhas do jogador, a partida é finalizada. A ideia é fornecer um campo de texto para receber a entrada do jogador, que deve ser um número, para fazer o comparativo com a conta matemática e devolver uma resposta de "correto" ou "incorreto", contabilizando os pontos com base nisso.

O jogo foi pensado para funcionar da seguinte forma:  
Logo após o cliente ser conectado ao servidor, o nome do jogador é solicitado para que se dê início ao jogo. Quando a entrada do jogador é recebida, ele irá escolher o modo de jogo (jogar sozinho ou contra um oponente). Portanto, se a escolha dele for jogar sozinho, poderá também escolher o nível de dificuldade, que pode ser fácil, normal, difícil ou especialista. Para o modo de jogo com um oponente, essa opção não é oferecida e o nível de dificuldade do jogo é fixado em normal.
