import pygame
import sys
import random
import time
import math

pygame.init() #prepara tutte le librerie interne (grafica, input, suono).
pygame.mixer.init() #inizializza il mixer audio

pygame.mixer.music.set_volume(0.5) #imposto il volume a 0.5 su 1.0


'''
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
DICHIARO VARIABILI
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
'''

WIDTH = 1530
HEIGHT = 800

#dichiaro i vari colori che mi servono
BLACK = (0,0,0)
WHITE = (255,255,255)
BK = (21, 67, 112)
ICE_BLUE = (151,193,230)
RED = (255,0,0)
BLU = (0,0,255)
GREEN = (0,255,0)
YELLOW = (255, 215, 0)

#creo la finestra e l'oggetto clock
screen = pygame.display.set_mode ((WIDTH, HEIGHT))
clock = pygame.time.Clock()

#dichiaro il fonte la grandezza del carattere per le eventuali scritte
font = pygame.font.Font(None, 36)

#dichiaro le varie variaibili che mi servono al di fuori del ciclo degli eventi
ICE_THICKNESS = 190
HEIGHT_W_ICE = HEIGHT - ICE_THICKNESS

vel_x = 0.0
vel_y = 0.0

GRAVITY = 2.5          # quanto tira giù
JUMP_FORCE = 35        # quanto salta in alto
on_ground = True       # parte appoggiato sul ghiaccio

sack = 0
delivered = 0
life = 3 # do 3 vite al giocatore

going_pg = "forward"
going_md = "backward"

INVINCIBILITY_DURATION = 2000 #imposto il tempo di durata della invincibilità
invincible = False
last_hit_time = 0

respawn = True

game_state = "rules"

medium_velocity = 3
c = 0 #serve per creare un timer parallelo a i tiks che mi serve poi per creare il moltiplicatore di velocità di medium (enemy)

life_add = 15 #serve per gestire l'incremento di vite una volta che si raccolgono 15 small (item)

n = 1 #mi serve per generare in modo casuale l'immagine di small (item)

set_state = True
difficulty = None

children_in_the_world = 2415319658
#children_in_the_world = 10

c1 = 0

diff_selected = False #mi serve per gestire l'avvio della musica solo una volta che si è scleta la difficoltà

# Lista per gestire le particelle dei fuochi d'artificio
firework_particles = []

start_music = True

'''
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
PARAMETRI ELEMENTI
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
'''

small = [3*12, 4*12] #dimensioni ostacolo piccolo (*... è il fattore di grandezza)
medium = [23*1.5, 63*1.5] #dimensioni ostacolo medio (*... è il fattore di grandezza)
big = [2*45, 3*45] #dimensioni ostacolo grande (*... è il fattore di grandezza)
pg = [3*24, 4*24] #simensioni giocatore (*... è il fattore di grandezza)

#dichiaro i parametri di spwan e di grandezza del giocatore
hit_box_player = 25 #più aumento questa varaibile più la hitbox diminuisce
y_p = HEIGHT_W_ICE-(pg[1]) #y di spawn del player: all'altezza del ghiaccio- l'altezza del player
W_P = pg[0] #larghezza del player
H_P = pg[1] #altezza del player

#dichiaro i parametri di spwan e di grandezza dell' item (small)
hit_box_small = 0
y_s = HEIGHT_W_ICE-(small[1])
W_S = small[0]
H_S = small[1]

#dichiaro i parametri di spwan e di grandezza dell'nemico (medium)
hit_box_medium = 15
y_m = HEIGHT_W_ICE-(medium[1])
W_M = medium[0]
H_M = medium[1]

#dichiaro i parametri di spwan e di grandezza dell'hub (big)
hit_box_big = 20
y_b = HEIGHT_W_ICE-(big[1])
W_B = big[0]
H_B = big[1]

#dichiaro i parametri di spawn e di grandezza del pavimento di ghiaccio
y_i = HEIGHT_W_ICE
W_I = WIDTH
H_I = ICE_THICKNESS
ice = pygame.Rect (0, y_i, W_I, H_I)

'''
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
DICHIARAZIONE FUNZIONI
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
'''

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#FUNZIONE RESET GIOCO
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def reset_game(): #resetto tutte le variabili ai valori iniziali
    global sack, delivered, life, c, c1, life_add, respawn, set_state, game_state, invincible, firework_particles, difficulty, diff_selected
    sack = 0
    delivered = 0
    life = 3
    c = 0
    c1 = 0
    life_add = 15
    respawn = True
    set_state = True
    game_state = "play"
    invincible = False
    firework_particles = []
    difficulty = None
    diff_selected = False
    pygame.mixer.music.stop() #fermo la musica in caso di reset per farla ripartire
    music_setter ("christmas carol.mp3")

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#FUNZIONE LAMPEGGIO TESTO
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def blink (txt = [], size = 80, times = 3, color = WHITE):
    y = HEIGHT // 2 - len(txt) * 18 #posiziono il testo al centro delle cordinate y

    for i in range (times): #per 3 volte:
        for line in txt:
            font_b = pygame.font.Font(None, size) #ingrandisco il font ad 80
            text = font_b.render (line, True, (color)) #creo un immagine "testo" con il testo "-1 LIFE"
            rect = text.get_rect(center=(WIDTH // 2, y))
            screen.blit (text, rect) #disegno l'immagine "text"
            pygame.display.flip() #flippo lo schermo mostrando l'immagine
            time.sleep (0.3) #aspetto 0.3 secondi
            text = font_b.render (line, True, BK) #cancello il testo
            screen.blit (text, rect) #disegno l'immagine "text"
            pygame.display.flip()
            time.sleep (0.1) #aspetto 0.1 seconi con il testo cancellato

    y += 36 #distanzio le righe di testo nel caso ce ne fosse più di una



#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#FUNZIONE CHE APPLICA LE IMMAGINI AI RETTANGOLI
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
IMM_LOADED = {} #creo un dizionario vuoto
def preload_all():
    files = [ #lista in cui metto tutte le immagini che ho scelto
        "player_forward (santa).png", "player_backward (santa).png",
        "medium_forward (grinch).png", "medium_backward (grinch).png",
        "big (tree).png", "background3.jpg", "background3_bottom.jpg"
    ]
    # Carico anche i regali da 1 a 7
    for i in range(1, 8):
        files.append(f"{i}.png") #per includere nella lista files tutti i 7 tipi di regali senza metterli a mano

    for f in files: #analizza tutti gli elementi della lsita file (tutti i nomi delle immagini)
        IMM_LOADED[f] = pygame.image.load(f).convert_alpha()
        #carico nel dizionario IMM_CARICATE tutte le immagini con etichetta il nome del file

preload_all() #eseguo la funzione (carico tutte le immagini)


def immage_applicator (name, W, H, x, y):
    if name in IMM_LOADED: #se il nome del file immagine che voglio caricare è un etichetta del dizionario IMM_CARICATE
        img = IMM_LOADED[name] #img prende il valore del contenuto dell'etichetta

    img_render = pygame.transform.scale(img, (W, H)) #metto in scala l'immagine rispetto al rettangolo
    screen.blit(img_render, (x, y)) #gli dico la posizione nel quale caricare l'immagine

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#VARIABILI E FUNZIONE CHE CREANO E ANIMANO I FIOCCHI DI NEVE
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
SNOW_COUNT = 200 #numero di fiocchi generati
snowflakes = [] #lista dove vado ad inserire i fiocchi di neve

for i in range(SNOW_COUNT):
    x = random.randint(0, WIDTH) #genero il fiocco di neve ad una x casuale nello schermo
    y = random.randint(-HEIGHT, 0) #genero il fiocco di neve ad una y causale sopra la cima dello schermo
    speed = random.uniform(1, 4) # velocità verticale (random.uniform estra un numero DECIAMEL casuale tra l'intervallo impostato)
    drift = random.uniform(-0.5, 0.5) # oscillazione per l'effetto vento
    radius = random.randint(2, 4)# dimensione casuale del fiocco

    snowflakes.append([x, y, speed, drift, radius]) #aggiungo all'interno della lista snowflakes un lista contenente le caratteristiche del fiocco di neve appena creato.
    '''
    Man mano che il ciclo si itera creo una lista di liste ciascuna delle quali contiene le caratteristiche di un siongolo fiocco di neve
    '''

def speed_bounderies_draw_flakes (list_snowflakes):
    for flake in list_snowflakes: #flake prende il valore della lista che rappresenta le caratteritiche di un singolo fiocco di neve
        flake[1] += flake[2] #aggiungo alla coridnata y del fiocco la velocità di caduta attribuita ad esso.
        flake[0] += flake[3] #aggiungo alla cordinata x del fiocco la velocità laterale di osccillazione (vento) attribuitagli.

        # se esce dallo schermo, ricompare dall'alto
        if flake[1] > HEIGHT: #se la cordinata y del fiocco sfora il bordo inferiore dello schermo
            flake[1] = random.randint(-50, -10) #riappare sopra la cima di esso.
            flake[0] = random.randint(0, WIDTH) #in una posizione x casuale
            #(praticamente le cordinate del fiocco vengono totalmente rigenerate, rimane uguale solo la dimensione)

    for flake in list_snowflakes: #analizza ogni lista di parametri (che rappresentano i singoli fiocchi di neve) nella lista
        pygame.draw.circle(screen, WHITE,(flake[0], flake[1]) ,flake[4]) #flake[4] rappresenta la grandezza, cioè il diamentro del fiocco, flake[0], flake[1] le cordinale x e y

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#FUNZIONI PER I FUOCHI D'ARTIFICIO (VITTORIA)
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def create_firework(x, y):
    #Crea 50 singole particelle per ogni esplosione
    for _ in range(50):
        #Sceglie un'angolazione casuale tra 0 e 360 gradi (espressa in radianti)
        angle = random.uniform(0, 2 * math.pi)

        #Sceglie una velocità casuale per la spinta iniziale dell'esplosione
        speed = random.uniform(3, 8)

        #TRIGONOMETRIA: Converte l'angolo e la velocità in spostamento X e Y
        #vc: velocità orizzontale, vy quella verticale
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed

        #Sceglie un colore a caso tra Rosso, Verde, Giallo o Bianco
        color = random.choice([RED, GREEN, YELLOW, WHITE])

        #Durata della particella: quanti "frame" vivrà prima di scomparire (da 30 a 60)
        life_p = random.randint(30, 60)

        #Aggiunge la particella alla lista globale. Ogni particella è una lista di dati:
        #[[posizione_x, posizione_y], [vel_x, vel_y], colore, durata_vita]
        firework_particles.append([[x, y], [vx, vy], color, life_p])


def update_fireworks():
    #Iteriamo su una copia della lista [:] per poter rimuovere elementi mentre cicliamo
    for p in firework_particles[:]:
        #Muove la particella aggiungendo la velocità alla posizione attuale
        p[0][0] += p[1][0] # Aggiorna X
        p[0][1] += p[1][1] # Aggiorna Y

        #EFFETTO GRAVITÀ: Aumenta la velocità verticale verso il basso ad ogni frame
        #Questo crea la tipica parabola cadente dei fuochi d'artificio
        p[1][1] += 0.1

        #Riduce la vita residua della particella
        p[3] -= 1

        #Se la vita è terminata, rimuove la particella dalla lista
        if p[3] <= 0:
            firework_particles.remove(p)
        else:
            #Se è ancora viva, la disegna come un piccolo cerchio di raggio 3
            pygame.draw.circle(screen, p[2], (int(p[0][0]), int(p[0][1])), 3)


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#FUNZIONE CHE STAMPA LE REGOLE A SCHERMO
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Gestisco la stampa a schermo delle regole
def draw_rules(screen, WIDTH, HEIGHT):
    screen.fill(BK)  # background
    #varie grandezze di font per varie parti del testo
    title_font = pygame.font.Font(None, 72)
    text_font = pygame.font.Font(None, 32)
    space_font = pygame.font.Font(None, 50)


    rules = [ #lista di stringhe
        "RULES",
        "",
        "1) Collect as many presents as possible.",
        "",
        "2) Deliver the presents to the Christmas Tree.",
        "   Be careful: once inside, escaping is not easy.",
        "",
        "3) You start with 3 lives.",
        "   The Grinch steals one when he catches you.",
        "   Every 15 delivered presents give you 1 extra life.",
        "",
        "4) The Grinch gets faster over time.",
        "   Stay alert and keep moving.",
        "",
        "5) You lose when you run out of lives.",
        "   You win if you deliver presents to",
        f"   all {children_in_the_world} children around the world.",
        "",
        "Can you save Christmas?",
        "",
        "PRESS SPACE TO START"
    ]

    y = HEIGHT // 2 - len(rules) * 18
    # HEIGHT // 2 trova il punto centrale esatto dello schermo in verticale
    # len(rules) restituisce in numero di righe nel testo delle regole
    # *18 ci da la spaziatura tra le righe

    for line in rules:
        if line == "RULES":  #se la riga di testo presa in questione è "RUELS", usa title_font (72)
            rendered_text = title_font.render(line, True, WHITE)

        elif line == "PRESS SPACE TO START":
            rendered_text = space_font.render(line, True, WHITE)

        else:
            rendered_text = text_font.render(line, True, WHITE)  #altrimenti usa text_font (32)

        rect = rendered_text.get_rect(center=(WIDTH // 2, y))
        #crea un rettangolo rect facendo si che il suo centro si trovi alle cordinate x = "WIDTH // 2" e y = HEIGHT // 2 - len(rules) * 18
        screen.blit(rendered_text, rect)
        y += 36


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#FUNZIONE CHE STAMPA A AL CENTRO DELLO SCHERMO UN QUALSIASI TESTO
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def text_center(screen, WIDTH, HEIGHT, text, font_size = 36, offset_y = 0):
    y = HEIGHT // 2 - len(text) * font_size/3
    # HEIGHT // 2 trova il punto centrale esatto dello schermo in verticale
    # len(text) restituisce in numero di righe nel testo
    # *18 ci da la spaziatura tra le righe
    font_obj = pygame.font.Font(None, font_size)
    for line in text:
        rendered_text = font_obj.render(line, True, WHITE)
        rect = rendered_text.get_rect(center=(WIDTH // 2, y-offset_y))
        # crea un rettangolo rect facendo si che il suo centro si trovi alle cordinate x ="WIDTH // 2" e y = ...
        screen.blit(rendered_text, rect)
        y += font_size

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#FUNZIONE PER CAMBIARE MUSICA IN BASE AI VARI STATI DEL GIOCO
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def music_setter (audio_file):
    pygame.mixer.music.load(audio_file)
    pygame.mixer.music.play(-1)  # -1 per riprodurre in loop


'''
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
GESTIONE CICLO EVENTI
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
'''
#avvio il cilo degli eventi:
running = True
while running == True:


    #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #GESTIONE EVENTI
    #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    for event in pygame.event.get():


        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        #EVENTO QUIT
        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

        if event.type == pygame.QUIT:
            running = False

        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        #EVENTO TASTO PREMUTO
        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        if event.type == pygame.KEYDOWN:

            #gestione caso stato regole
            if game_state == "rules":
                if event.key == pygame.K_SPACE:
                    game_state = "play" # Passa allo stato play che mi permette, se set_state è ancora true, di selezionare le difficoltà, se set_state è false di continuare con il gioco

            #selezione difficoltà
            elif game_state == "play" and set_state == True:
                if event.key == pygame.K_1:
                    difficulty = 1
                    set_state = False

                elif event.key == pygame.K_2:
                    difficulty = 2
                    set_state = False

                elif event.key == pygame.K_3:
                    difficulty = 3
                    set_state = False

                elif event.key == pygame.K_4:
                    difficulty = 4
                    set_state = False


            #gestione salto (se si entra nel gioco vero e proprio)
            elif game_state == "play" and set_state == False: #se siamo in play ma non stiamo più trattando la selezione delle difficoltà:
                if event.key == pygame.K_SPACE or event.key == pygame.K_UP or event.key == pygame.K_w:
                    if on_ground:           # salta solo se è a terra (per evitarte che tenendo premuto inizio a volare)
                        vel_y = -JUMP_FORCE # alla velocità y aggiungo la forza di salto
                        on_ground = False # mi alzo dal suolo

            #gestione restart negli stati game over e victory
            elif game_state == "game over" or game_state == "victory":
                if event.key == pygame.K_r: #re premo r
                    reset_game() #resetto i parametri
                if event.key == pygame.K_ESCAPE: #se premo ESC(ape)
                    running = False #chiudo la finestra di pygame


    #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #DISEGNO REGOLE
    #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    if game_state == "rules":
        draw_rules(screen, WIDTH, HEIGHT)

    #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #AVVIAMENTO GIOCO VERO E PROPRIO
    #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    elif game_state == "play":


        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        #DISEGNO DIFFICOLTA'
        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

        if set_state == True: #Modalità di selezione difficoltà
            screen.fill(BK) #riempio il mio shcermo del colore di sfondo
            speed_bounderies_draw_flakes (snowflakes) #disegno i fiocchi di neve anche nella selezione
            text_center(screen, WIDTH, HEIGHT, text = ["Set difficulty:", "1 Easy", "2 Normal", "3 Hard", "4 Impossible"], font_size = 100) #disegno al centro il testo


        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        #ESECUZIONE GIOCO
        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

        elif set_state == False: #Modalità di gioco attivo
            if (difficulty == 1 or difficulty == 2 or difficulty == 3 or difficulty == 4) and c1 <= 120: #se ho selezionato la difficoltà e non sono passati ancora 2 secondi (c1 <= 120)
                screen.fill (BK)

                if difficulty == 1:
                    txt_difficulty = "Easy"
                    max_multiplier = 12

                elif difficulty == 2:
                    txt_difficulty = "Medium"
                    max_multiplier = 7

                elif difficulty == 3:
                    txt_difficulty = "Hard"
                    max_multiplier = 5 
                    
                elif difficulty == 4:
                    txt_difficulty = "Impossible"
                    max_multiplier = 4.5
                 
                c1 += 1 #è come se creassi mini loop dove il valore di c1=60 = 1 secondo scandisce la sua durata, mi serve per fare una pausa e fare visualizzare la difficoltà selezionata
                text_center(screen, WIDTH, HEIGHT, text = [f"Difficulty set: {txt_difficulty}"], font_size = 150, offset_y = 0)
                speed_bounderies_draw_flakes (snowflakes) #continuo a fare cadere i fiocchi anche nel mini ciclo
                pygame.display.flip() #mostro quello che ho disegnato
                clock.tick(60) #imposto gli FPS
                continue #continua (salta tutto il codice successivo) fino a che non passano due secondi. 


            #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            #ESECUZIONE TEMPO, COUNTER E MOLTIPLICATORE
            #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            ticks = pygame.time.get_ticks()
            seconds = ticks // 1000 # dato che i ticks sono espressi in millesecondo divido per 1000 convertendo in secondi
            c += 1
            counter = c /60 # counter è un altro modo per contare i secondi indipendente dal ticks, mi serve per creare il moltiplicatrore che poi azzero quando si perde una vita

            if start_music == True:
                 music_setter ("christmas carol.mp3") #imposto questo di base
                 start_music = False
            #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            #RESPAWN ALLE CORDINATE INIZIALI DEI VARI OGGETTI IN CASO SI PERDA UNA VITA
            #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            if respawn == True:
                player = pygame.Rect (0+hit_box_player, y_p, W_P-hit_box_player, H_P) # resetto i parametri di spawn (x = 0, y = y_p) di player

                x_spawn = random.randint(0, WIDTH-W_S) # faccio spawnare l'oggetto small (collezionabile) ad una x casuale
                small_rect = pygame.Rect (x_spawn , y_s, W_S-hit_box_small, H_S) # resetto i parametri di spawn di small

                medium_rect = pygame.Rect (WIDTH-W_M, y_m, W_M-hit_box_medium, H_M) # resetto i parametri di spawn di medium

                big_rect = pygame.Rect ((WIDTH/2)-(W_B/2), y_b, W_B-hit_box_big, H_B) # resetto i parametri di spawn di big (l'albero)

                vel_x = 0.0 # resetto i parametri di velocità
                vel_y = 0.0

                respawn = False


            #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            #MOVIMENTO DEL PERONAGGIO E FISICA
            #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            vel_x *= 0.92          # scivola orizzontalmente
            vel_y += GRAVITY       # gravità verso il basso

            #gestione tasti premuti
            keys = pygame.key.get_pressed()
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]: # se premo freccia a destra o "d":
                vel_x += 1.4 # aumento la velocità
                going_pg = "forward" # faccio diventare lo stato del player "forward" = immagine che guarda in avanti

            if keys[pygame.K_a] or keys[pygame.K_LEFT]: # se premo freccia a sinistra o "a":
                vel_x -= 1.4 # diminuisco la velocità
                going_pg = "backward" # faccio diventare lo stato del player "backward" = immagine che guarda in dietro

            #applico la velocità alle cordinate del player
            player.x += int(vel_x)
            player.y += int(vel_y)



            #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            #MOVIMENTO DEL NEMICO E APPLICAZIONE DEL MOLTIPLICATORE
            #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            multiplier = min (max_multiplier , (2+counter/medium_velocity)) # aggiungo un fattore moltiplicatore che andrà ad aumentare la velocità dell'enemy (medium) con il passare del tempo
            dx = player.x - medium_rect.x # distanza orizzontale in pixel tra il player e l'enemy (medium)
            dy = player.y - medium_rect.y # distanza verticale in pixel tra il player e l'enemy
            dist = max(1, (dx*dx + dy*dy)**0.5) # calcolo la distanza effettiva con il teorema di pitagora (**0.5 = sqrt). max()... serve per evitare la divisione per 0 nel prossimo passaggio
            medium_rect.x += (dx / dist * difficulty)*multiplier # dx (o dy) / dist ci da la direzione verso la quale il player dovrebbe muoversi
            if (dx / dist * difficulty) < 0:
                going_md = "backward"
            elif (dx / dist * difficulty) > 0:
                going_md = "forward"

            '''
            ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            COLLISIONI
            --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            '''

            #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            #COLLISIONE PLAYER-ITEM E ITEM-HUB (per non far spwnare l'item dentro l'hub)
            #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            if player.colliderect(small_rect) or small_rect.colliderect(big_rect): # se il player e l'oggetto da raccogliere (small) si toccano o se l'oggetto (small) spwna dentro l'hub (big):
                x_spawn = random.randint(0, WIDTH-W_S) # l'oggetto da raccogliere (small) viene rigenerato con una x causale
                n = random.randint (1,7) # serve per generare una tipologia di small casuale
                small_rect = pygame.Rect (x_spawn , y_s, W_S, H_S)
                sack += 1 # aumento il counter di 1

            #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            #COLLISIONE PLAYER - HUB (consegna item e incastraggio nell'hub)
            #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            if player.colliderect(big_rect): # se il player tocca l'hub (big) aggiunge il numero di oggetti (small) che aveva nel sacco
                delivered += sack
                vel_x = 0 # faccio l'effetto ragnatela
                sack = 0 # azzero gli item (small) che ha il player

            #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            #COLLISIONE PLAYER - NEMICO (perdita vita, invincibilità, reset moltiplicatore(c = 0))
            #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            if player.colliderect(medium_rect) and invincible == False: # se il player e il l'oggetto che rincorre (medium) si scontrano e il player non è invincibile
                life -= 1 # togli una vita
                sack = 0
                invincible = True # rendi il player invincibile
                last_hit_time = ticks # assegna alla variabile ticks il momento in cui il player è diventato invincibile
                respawn = True
                c = 0 # azzero c = riazzero counter = azzero multiplier = reimposto la velocità di medium
                if life > 0:
                    music_setter ("x3_game_over.MP3")
                    blink (txt = ["-1 LIFE!!!"], size = 200, times = 3, color = WHITE)
                    music_setter ("christmas carol.mp3")

            '''
            ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            LOGICA DI GIOCO
            --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            '''
            #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            #CALCOLO INVINCIBILITA'
            #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            if last_hit_time+INVINCIBILITY_DURATION <= ticks: # se il momento che il player è diventato incincibile + la durata dell'invincibilità sono minori del tempo attuale = è passato il tempo invincibilità
                invincible = False # tolgo l'invincibilità al player


            #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            #MECCANISMO DI INCREMENTO VITE
            #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            if delivered >= life_add: # se i pacchi consegnati sono superiori a life_add (che ongi volta che viene verificato aumenta di 15)
                life += 1 # aggiungi una vita
                life_add += 15 # aggiungi 15 a life_add


            #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            #CASISITICA DI PERDITA DI TUTTE LE VITE O VITTORIA
            #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            if life <= 0: # se ho finito le vite
                game_state = "game over"
                music_setter ("x3_game_over.MP3") #imposto musica (suono) di gameover
                

            if children_in_the_world - delivered <= 0: # se i bambini da servire sono finiti
                game_state = "victory"
                music_setter ("jingle bells arcade.mp3") #imposto musica di vittoria

                


            '''
            ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            CONFINI DEGLI ELEMENTI
            --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            '''
            #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            #BLOCCO PLAYER NEI CONFINI DELLO SCHERMO
            #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            if player.x < 0: # se la x di player diventa minore di 0 = è uscita dallo schermo
                player.x = 0 # riporto la x a 0 = riporto la x dentro lo schermo
            if player.x > WIDTH - player.width: # se il lato destro del rettangolo esce dallo schermo
                player.x = WIDTH - player.width # riporto il lato destro dentro lo schermo

            if player.y < 0:
                player.y = 0
            if player.y > HEIGHT - player.height:
                player.y = HEIGHT - player.height

            #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            #BLOCCO PLAYER SUL PAVIMENTO DI GHIACCIO
            #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            if player.bottom >= HEIGHT_W_ICE: # se il player è a terra
                player.bottom = HEIGHT_W_ICE # gli impongo che non può andare più in basso della pavimento di ghiaccio
                vel_y = 0 # azzero anche la velocità di movimento nella direzione y
                on_ground = True # sono a terra


            '''
            ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            DISEGNO OGGETTI E SCRITTE
            --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            '''
            #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            #DISEGNO NEVE (e hitbox degli oggetti se si tolgono le virgolete commentratrici)
            #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            #screen.fill (BK)
            immage_applicator (name = "background3.jpg", W = WIDTH, H = HEIGHT, x = 0, y = 0) #al posto di usare screen.fill utilizzo un immagine cos' da creare un effetto sfondo diverso da un colore monotono
            speed_bounderies_draw_flakes (snowflakes)

            '''
            pygame.draw.rect (screen, ICE_BLUE, ice) #disegno la lastra di ghiaccio
            pygame.draw.rect (screen, WHITE, player)
            pygame.draw.rect (screen, WHITE, small_rect)
            pygame.draw.rect (screen, WHITE, medium_rect)
            pygame.draw.rect (screen, WHITE, big_rect)
            '''



            #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            #DISEGNO SCRITTE
            #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            #Stampa delle scritte
            txt_timer = font.render (f"Playing for: {seconds}s", True, (255,255,255))
            screen.blit (txt_timer, (WIDTH-(WIDTH-10), (HEIGHT-(HEIGHT-10)) ))

            txt_life = font.render (f"Life: {life}", True, (255,255,255))
            screen.blit (txt_life, (WIDTH-(WIDTH-10), (HEIGHT-(HEIGHT-40)) ))

            txt_sack = font.render (f"Presents in the sack: {sack}", True, (255,255,255))
            screen.blit (txt_sack, (WIDTH-(WIDTH-10), (HEIGHT-(HEIGHT-70)) ))

            txt_delivered = font.render (f"Delivered presents: {delivered}", True, (255,255,255))
            screen.blit (txt_delivered, (WIDTH-(WIDTH-10), (HEIGHT-(HEIGHT-100)) ))

            txt_diff = font.render (f"Difficulty set: {txt_difficulty}", True, (255,255,255))
            screen.blit (txt_diff, (WIDTH-(WIDTH-10), (HEIGHT-(HEIGHT-130)) ))

            text_center(screen, WIDTH, HEIGHT, text = [f"Presents left to deliver: {children_in_the_world-delivered}"], font_size = 80, offset_y = 150)

            '''
            ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            APPLICAZIONE DELLE IMAMGINI (già caricate, non le devo ricaricare ogni volta dal disco)
            --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            '''
            if going_pg == "forward": # se lo stato del player è forward: disegno l'immagine che guarda in avanti
                immage_applicator (name = "player_forward (santa).png", W = W_P, H = H_P , x = player.x-hit_box_player+5, y = player.y) #-hit_box_player: escludo il sacco dalla hitbox. +5: escludop la mano dalla hitbox
            elif going_pg == "backward": # se lo stato del player è backward: disegno l'immagine che guarda in dietro
                immage_applicator (name = "player_backward (santa).png", W = W_P, H = H_P , x = player.x-5, y = player.y) #-5: escludo la mano dalla hitbox

            # Immagini Small (item)
            immage_applicator (name = f"{n}.png", W = W_S, H = H_S , x = small_rect.x, y = small_rect.y)

            # Immagine Medium (Grinch)
            if going_md == "forward":
                immage_applicator (name = "medium_forward (grinch).png", W = W_M, H = H_M , x = medium_rect.x-(hit_box_medium/2), y = medium_rect.y) #(hit_box_medium/2): centro l'immagine alla hitbox
            elif going_md == "backward":
                immage_applicator (name = "medium_backward (grinch).png", W = W_M, H = H_M , x = medium_rect.x-(hit_box_medium/2), y = medium_rect.y)

            # Immagine Big (Tree)
            immage_applicator (name = "big (tree).png", W = W_B, H = H_B, x = big_rect.x-(hit_box_big/2), y = big_rect.y)
            
            # Immagine di maschera del pavimetno per coprire la neve
            immage_applicator (name = "background3_bottom.jpg", W = W_I, H = H_I, x = 0, y = y_i)



    #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #GESTIONE GAME_STATE = "GAME OVER"
    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    elif game_state == "game over":
        screen.fill(BK)
        speed_bounderies_draw_flakes(snowflakes)
        text_center(screen, WIDTH, HEIGHT, text=["GAME OVER!!!", "The Grinch stole Christmas..."], font_size=100)
        text_center(screen, WIDTH, HEIGHT, text=["Press R to Restart", "Press ESC to Quit"], font_size=50, offset_y=-200)

    #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #GESTIONE GAME_STATE = "VICTORY" (FUOCHI D'ARTIFICIO)
    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    elif game_state == "victory":
        #screen.fill(BK)
        immage_applicator (name = "background3.png", W = WIDTH, H = HEIGHT, x = 0, y = 0)
        speed_bounderies_draw_flakes(snowflakes) # Continua a nevicare

        # Genera fuochi d'artificio casuali
        if random.randint(1,100) < 10: #nel 10% dei casi:
            create_firework(random.randint(100, WIDTH-100), random.randint(100, HEIGHT-300)) #genero i fuochi di artificio a cordinata casuali nello schermo

        update_fireworks()# aggiorno (gestisco il movimento), dei fuochi d'artificio

        # Scritta di Vittoria
        text_center(screen, WIDTH, HEIGHT, text=["YOU SAVED CHRISTMAS!", "Every child has their present."], font_size=100)
        text_center(screen, WIDTH, HEIGHT, text=["Press R to Restart", "Press ESC to Exit"], font_size=40, offset_y=-250)

    '''
    ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    AGGIORNAMENTO DEL FRAME E CLOCK
    --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    '''
    if running:
        pygame.display.flip() # mostro tutto quello che ho disegnato nel frame
        clock.tick(60) #imposto gli FPS

pygame.quit() #eseguo la chiusura della finestra solo quando si è usciti dal ciclo, ergo si ha premuto X
sys.exit()
