#importando a biblioteca pygame para desenvolvimento do jogo e biblioteca threading e time!(memory pro pra medi a quantidade de uso da memory
import pygame
import threading
import time
#from memory_profiler import profile

# Inicializando o pygame
pygame.init()

# Criando a janela do jogo com dimensões 1280x720 pixels
window = pygame.display.set_mode([1280, 720])

# Configurando o título da janela
title = pygame.display.set_caption('Futebol Pong')  #nome da janela

# Carregando imagens necessárias
win = pygame.image.load('assets/win.png')# carrega img de vitoria
score1_img = pygame.image.load('assets/score/0.png')# carrega img do placar1
score2_img = pygame.image.load('assets/score/0.png')# carrega img do placa2
field = pygame.image.load('assets/field.png')  # carrega img do campo
player1 = pygame.image.load('assets/player1.png')  # carrega player1
player2 = pygame.image.load('assets/player2.png')  # carrega player2
ball = pygame.image.load('assets/ball.png')  # carrega bola

# Configurando variáveis iniciais
player1_y = 310 #310 valor onde eles está sendo desenhado
player1_moveup = False # vars pra verificar dps se o jogador1 está segurando ou nao a tecla
player1_movedown = False

player2_y = 310

ball_x = 617 #posi da bola eixo x
ball_y = 337 #pósi da bola no eixo Y
ball_dir = 0 #velocidade inicial da bola
ball_dir_y = 1# direção inicial da bola

score1 = 0 #valores iniciais do placar
score2 = 0

# Semáforo para controlar o acesso aos recursos compartilhados
player1_semaphore = threading.Semaphore(1)
player2_semaphore = threading.Semaphore(1)
att_semaphore = threading.Semaphore(1)
# Variável para armazenar o tempo decorrido
elapsed_time = 0

"""# Função para mostrar mensagens de utilização da thread
def print_thread_usage(move_player2_thread):
    print(f"Thread {move_player2_thread} em execução.")

# Função para mostrar mensagens de utilização do semáforo
def print_semaphore_usage(att_semaphore, action):
    print(f"Semaforo {att_semaphore} {action}.")"""

# Função para mover o player1
def move_player():
    global player1_y

    player1_semaphore.acquire()
    player1_y = ball_y # para jogar sozin só remover essa linha

    if player1_moveup: # se essa var for verdadeira
        player1_y -= 20 # player1 vai sub - 20pixei
    elif player1_movedown:
        player1_y += 20

    if player1_y <= 0:  # define limites do player1 na tela
        player1_y = 0
    elif player1_y >= 575:
        player1_y = 575

    player1_semaphore.release()


# Função para mover o player2 em uma thread separada
def move_player2():
    global player2_y

    #player2_semaphore.acquire()
    player2_y = ball_y

    if player2_y <= 0:  # define limites do player2 na tela
        player2_y = 0
    elif player2_y >= 575:
        player2_y = 575
    #player2_semaphore.release()


#@profile
def move_player2_thread():
    global player2_y

    while True:
        #print_semaphore_usage("player2_semaphore", "adquirido")
       # Bloqueia o acesso à seção crítica usando o semáforo
        player2_semaphore.acquire()

        #print_thread_usage("move_player2_thread")

        move_player2()

        # Libera o acesso à seção crítica
        player2_semaphore.release()
        #print_semaphore_usage("player2_semaphore", "liberado")

    time.sleep(0.01)


# Função para aumentar a velocidade da bola em 2x a cada 5 segundos
def increase_ball_speed():
    global ball_dir, ball_dir_y, elapsed_time

    while True:
        time.sleep(1)  # Espera 1 segundo
        elapsed_time += 1

        if elapsed_time == 5:
            #print_thread_usage("increase_ball_speed")
            ball_dir *= 1.5
            ball_dir_y *= 1.5
            elapsed_time = 0

# Iniciando a thread para o movimento do player2
player2_thread = threading.Thread(target=move_player2_thread)
player2_thread.daemon = True
player2_thread.start()


# Iniciando a thread para aumentar a velocidade da bola
speed_thread = threading.Thread(target=increase_ball_speed)
speed_thread.daemon = True
speed_thread.start()


# Função para mover a bola e verificar colisões
#@profile
def move_ball():
    global ball_x, ball_y, ball_dir, ball_dir_y, score1, score2, score1_img, score2_img #chamando as var glb

    ball_x += ball_dir
    ball_y += ball_dir_y

    # Verificando colisões com as raquetes dos jogadores
    if ball_x < 120:
        if player1_y < ball_y + 23:
            if player1_y + 146 > ball_y:
                ball_dir *= -1

    if ball_x > 1100:
        if player2_y < ball_y + 23:
            if player2_y + 146 > ball_y:
                ball_dir *= -1

    # Verificando colisões com as bordas superior e inferior
    if ball_y > 685:
        ball_dir_y *= -1
    elif ball_y <= 0:
        ball_dir_y *= -1

    # Verificando se a bola ultrapassou os limites laterais
    if ball_x < -50:
        ball_x = 617
        ball_y = 337
        ball_dir_y *= -1
        ball_dir *= -1
        score2 += 1
        score2_img = pygame.image.load('assets/score/' + str(score2) + '.png')
    elif ball_x > 1320:
        ball_x = 617
        ball_y = 337
        ball_dir_y *= -1
        ball_dir *= -1
        score1 += 1
        score1_img = pygame.image.load('assets/score/' + str(score1) + '.png')



# Função para desenhar elementos na tela
#@profile
def draw():
    if score1 or score2 < 9:
        window.blit(field, (0, 0))
        window.blit(player1, (50, player1_y)) #var n modificadas então desconsiderar global
        window.blit(player2, (1150, player2_y))
        window.blit(ball, (ball_x, ball_y))
        window.blit(score1_img, (500, 50)) #desenha elementos n tela nas posições definidas
        window.blit(score2_img, (710, 50))
        move_ball()
        move_player()
    else:
        window.blit(win, (300, 330))


def update_ui_thread():
    while True:
        att_semaphore.acquire()
        pygame.display.update()

        time.sleep(0.1)
        att_semaphore.release()
# Inicie a thread para atualizações gráficas
update_ui_thread = threading.Thread(target=update_ui_thread)
update_ui_thread.daemon = True
update_ui_thread.start()

# Loop principal do jogo / esta parte do código que foi definido as movimentações do jogador

loop = True
while loop:
    # Verificando eventos
    for events in pygame.event.get():
        if events.type == pygame.QUIT:
            loop = False  # evento para fechar a tela no botão fechar da janela

        if events.type == pygame.KEYDOWN:  # condição para tecla
            if events.key == pygame.K_w:  # se o tipo do evento for = K_W
                player1_semaphore.acquire()
                player1_moveup = True  # personagem se move com tecla segurada
                player1_semaphore.release()
            if events.key == pygame.K_s:
                player1_semaphore.acquire()
                player1_movedown = True
                player1_semaphore.release()

        if events.type == pygame.KEYUP:  # condição que garante se a tecla está sendo pressionada - no caso aqui é false, o player não se move se a tecla for solta
            if events.key == pygame.K_w:
                player1_semaphore.acquire()
                player1_moveup = False
                player1_semaphore.release()
            if events.key == pygame.K_s:
                player1_semaphore.acquire()
                player1_movedown = False
                player1_semaphore.release()

    move_player2()


    draw()  # chamando função draw para desenhar elementos na tela

    #time.sleep(0.01)
    pygame.display.update()  # atualiza sempre a tela


