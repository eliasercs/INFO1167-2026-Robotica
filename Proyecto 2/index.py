import numpy as np
import pygame
import random as ra
import sys

meta = (5, 3)
muralla = (2, 3)

nU = 0.0001
pE = 0.9
pF = 1 - pE

pD1 = pF / 2
pD2 = pF / 2

landa = 0.97

TIEMPOS_MEDIOS = {
    "N": 2,
    "S": 2,
    "E": 3,
    "O": 3
}

aP = [
    (0, 1), (0, 2), (0, 3), (0, 4),
    (1, 1), (1, 4),
    (2, 0), (2, 1), (2, 2), (2, 4), (2, 5), (2, 6),
    (3, 2), (3, 4),
    (4, 2), (4, 3), (4, 4),
    meta
]

aA = ["N", "S", "E", "O"]

laberinto = np.full((6, 7), "#", dtype=str)

for p in aP:
    laberinto[p] = "p"

laberinto[meta] = "M"
laberinto[muralla] = "X"

nMapH = len(laberinto)
nMapW = len(laberinto[0])

nS = len(aP)
nA = len(aA)

coord_to_state = {pos: idx for idx, pos in enumerate(aP)}

def set_rewards():
    rewards = {
        "p": -0.1,
        "M": 5
    }

    rewards_s = []

    for i, j in aP:
        rewards_s.append(rewards[laberinto[i][j]])

    return rewards_s

rWDs = set_rewards()

def obtener_tiempo(direccion):
    if direccion in ("N", "S"):
        return max(0.1, np.random.normal(2, 0.2))
    else:
        return max(0.1, np.random.normal(3, 0.3))

verificar_posiciones_invalidas = {
    "n": lambda i, j: i - 1 < 0,
    "s": lambda i, j: i + 1 >= len(laberinto),
    "e": lambda i, j: j + 1 >= len(laberinto[0]),
    "o": lambda i, j: j - 1 < 0
}

verificar_desvio_1 = {
    "n": lambda i, j: j + 1 < len(laberinto[i]),
    "s": lambda i, j: j + 1 < len(laberinto[i]),
    "e": lambda i, j: i + 1 < len(laberinto),
    "o": lambda i, j: i + 1 < len(laberinto)
}

verificar_desvio_2 = {
    "n": lambda i, j: j - 1 >= 0,
    "s": lambda i, j: j - 1 >= 0,
    "e": lambda i, j: i - 1 >= 0,
    "o": lambda i, j: i - 1 >= 0
}

obtener_coord_exito = {
    "n": lambda i, j: (i - 1, j),
    "s": lambda i, j: (i + 1, j),
    "e": lambda i, j: (i, j + 1),
    "o": lambda i, j: (i, j - 1)
}

obtener_coord_desvio1 = {
    "n": lambda i, j: (i, j + 1),
    "s": lambda i, j: (i, j + 1),
    "e": lambda i, j: (i + 1, j),
    "o": lambda i, j: (i + 1, j)
}

obtener_coord_desvio2 = {
    "n": lambda i, j: (i, j - 1),
    "s": lambda i, j: (i, j - 1),
    "e": lambda i, j: (i - 1, j),
    "o": lambda i, j: (i - 1, j)
}

def crear_matriz_transicion(direccion):
    matriz_t = np.zeros((nS, nS))
    transitable = ["p", "M"]

    for i in range(len(laberinto)):
        for j in range(len(laberinto[i])):
            celda_actual = laberinto[i][j]

            if celda_actual not in transitable:
                continue

            estado_actual = coord_to_state.get((i, j), -1)

            if estado_actual == -1:
                continue

            if (i, j) == meta:
                matriz_t[estado_actual][estado_actual] = 1
                continue

            error = 0
            estado_objetivo = -1
            estado_desvio1 = -1
            estado_desvio2 = -1

            exito = 0
            desvio1 = 0
            desvio2 = 0

            if not verificar_posiciones_invalidas[direccion](i, j):
                coord_objetivo = obtener_coord_exito[direccion](i, j)
                celda_objetivo = laberinto[coord_objetivo[0]][coord_objetivo[1]]

                if celda_objetivo in transitable:
                    estado_objetivo = coord_to_state.get(coord_objetivo, -1)
                    exito = pE
                else:
                    error += pE
            else:
                error += pE

            if verificar_desvio_1[direccion](i, j):
                coord_desvio1 = obtener_coord_desvio1[direccion](i, j)
                celda_desvio1 = laberinto[coord_desvio1[0]][coord_desvio1[1]]

                if celda_desvio1 in transitable:
                    estado_desvio1 = coord_to_state.get(coord_desvio1, -1)
                    desvio1 = pD1
                else:
                    error += pD1
            else:
                error += pD1

            if verificar_desvio_2[direccion](i, j):
                coord_desvio2 = obtener_coord_desvio2[direccion](i, j)
                celda_desvio2 = laberinto[coord_desvio2[0]][coord_desvio2[1]]

                if celda_desvio2 in transitable:
                    estado_desvio2 = coord_to_state.get(coord_desvio2, -1)
                    desvio2 = pD2
                else:
                    error += pD2
            else:
                error += pD2

            matriz_t[estado_actual][estado_actual] = error

            if estado_objetivo != -1:
                matriz_t[estado_actual][estado_objetivo] = exito

            if estado_desvio1 != -1:
                matriz_t[estado_actual][estado_desvio1] = desvio1

            if estado_desvio2 != -1:
                matriz_t[estado_actual][estado_desvio2] = desvio2

    return matriz_t

aT = [
    crear_matriz_transicion("n"),
    crear_matriz_transicion("s"),
    crear_matriz_transicion("e"),
    crear_matriz_transicion("o")
]

def valueIteration(aE, modo):
    aPol = [0] * nS
    aE = aE.copy()

    while True:
        aE_next = [0] * nS

        for s in range(nS):
            max_value = float("-inf")

            for a in range(nA):
                if modo == "MDP":
                    descuento = landa
                else:
                    accion = aA[a]
                    descuento = landa ** TIEMPOS_MEDIOS[accion]

                value = rWDs[s] + descuento * sum(
                    aT[a][s][i] * aE[i] for i in range(nS)
                )

                if value > max_value:
                    max_value = value
                    aPol[s] = a

            aE_next[s] = max_value

        if all(abs(aE_next[i] - aE[i]) < nU for i in range(nS)):
            break

        aE = aE_next

    aPol_final = [aA[aPol[i]] for i in range(nS)]
    return aPol_final

aE_inicial = [0] * nS

aPol_mdp = valueIteration(aE_inicial, "MDP")
aPol_smdp = valueIteration(aE_inicial, "SMDP")

coord_accion_mdp = {aP[i]: aPol_mdp[i] for i in range(len(aP))}
coord_accion_smdp = {aP[i]: aPol_smdp[i] for i in range(len(aP))}

print("Política MDP:", aPol_mdp)
print("Política SMDP:", aPol_smdp)

class Agente:
    def __init__(self, pos_inicial):
        self.pos = pos_inicial
        self.ultimo_tiempo = 0
        self.termino = False
        self.proximo_movimiento = 0

    def mover(self, direccion, modo):
        if self.termino:
            return

        if self.pos == meta:
            self.termino = True
            return

        if modo == "SMDP":
            self.ultimo_tiempo = obtener_tiempo(direccion)
            print(f"SMDP | Acción: {direccion} | Tiempo: {self.ultimo_tiempo:.2f}")
        else:
            self.ultimo_tiempo = 1
            print(f"MDP  | Acción: {direccion}")

        resultado = np.random.choice(
            ["fallo 1", "exito", "fallo 2"],
            p=(pD1, pE, pD2)
        )

        arrNP = list(self.pos)

        if direccion == "N":
            if resultado == "exito":
                arrNP = [self.pos[0] - 1, self.pos[1]]
            elif resultado == "fallo 1":
                arrNP = [self.pos[0], self.pos[1] - 1]
            else:
                arrNP = [self.pos[0], self.pos[1] + 1]

        elif direccion == "S":
            if resultado == "exito":
                arrNP = [self.pos[0] + 1, self.pos[1]]
            elif resultado == "fallo 1":
                arrNP = [self.pos[0], self.pos[1] - 1]
            else:
                arrNP = [self.pos[0], self.pos[1] + 1]

        elif direccion == "E":
            if resultado == "exito":
                arrNP = [self.pos[0], self.pos[1] + 1]
            elif resultado == "fallo 1":
                arrNP = [self.pos[0] - 1, self.pos[1]]
            else:
                arrNP = [self.pos[0] + 1, self.pos[1]]

        elif direccion == "O":
            if resultado == "exito":
                arrNP = [self.pos[0], self.pos[1] - 1]
            elif resultado == "fallo 1":
                arrNP = [self.pos[0] - 1, self.pos[1]]
            else:
                arrNP = [self.pos[0] + 1, self.pos[1]]

        if (
            0 <= arrNP[0] < nMapH and
            0 <= arrNP[1] < nMapW and
            laberinto[arrNP[0]][arrNP[1]] in ["p", "M"]
        ):
            self.pos = tuple(arrNP)

        if self.pos == meta:
            self.termino = True

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
SKY_BLUE = (207, 231, 245)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

nCS = 70

MARGEN_SUPERIOR = 70
SEPARACION = 80

SCREEN_WIDTH = nMapW * nCS * 2 + SEPARACION
SCREEN_HEIGHT = nMapH * nCS + MARGEN_SUPERIOR

pygame.init()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Proyecto #2 - INFO1167")

flecha_n = pygame.image.load("assets/N.png").convert_alpha()
flecha_s = pygame.image.load("assets/S.png").convert_alpha()
flecha_e = pygame.image.load("assets/E.png").convert_alpha()
flecha_o = pygame.image.load("assets/O.png").convert_alpha()

TAM_FLECHA = 48

flecha_n = pygame.transform.smoothscale(flecha_n, (TAM_FLECHA, TAM_FLECHA))
flecha_s = pygame.transform.smoothscale(flecha_s, (TAM_FLECHA, TAM_FLECHA))
flecha_e = pygame.transform.smoothscale(flecha_e, (TAM_FLECHA, TAM_FLECHA))
flecha_o = pygame.transform.smoothscale(flecha_o, (TAM_FLECHA, TAM_FLECHA))

flechas = {
    "N": flecha_n,
    "S": flecha_s,
    "E": flecha_e,
    "O": flecha_o
}

fuente_titulo = pygame.font.SysFont(None, 36)
fuente_info = pygame.font.SysFont(None, 24)

def dibujar_laberinto(offset_x, titulo, politica, agente, modo):
    texto = fuente_titulo.render(titulo, True, BLACK)
    screen.blit(texto, (offset_x + 10, 10))

    if agente.termino:
        info = "Llegó a la meta"
    elif modo == "SMDP":
        info = f"Tiempo acción: {agente.ultimo_tiempo:.2f}"
    else:
        info = "Tiempo fijo"

    texto_info = fuente_info.render(info, True, BLACK)
    screen.blit(texto_info, (offset_x + 10, 40))

    for row in range(len(laberinto)):
        for col in range(len(laberinto[row])):
            celda_actual = laberinto[row][col]

            x = offset_x + col * nCS
            y = MARGEN_SUPERIOR + row * nCS

            celda = pygame.Rect(x, y, nCS, nCS)

            if celda_actual == "X":
                pygame.draw.rect(screen, GRAY, celda)
            elif celda_actual == "M":
                pygame.draw.rect(screen, GREEN, celda)
            elif celda_actual == "p":
                pygame.draw.rect(screen, SKY_BLUE, celda)
            else:
                pygame.draw.rect(screen, WHITE, celda)

            pygame.draw.rect(screen, BLACK, celda, 1)

            if celda_actual == "p":
                accion = politica.get((row, col), "")
                if accion in flechas:
                    img_flecha = flechas[accion]
                    screen.blit(
                        img_flecha,
                        (x + (nCS - TAM_FLECHA) // 2, y + (nCS - TAM_FLECHA) // 2)
                    )

    cx = offset_x + agente.pos[1] * nCS + nCS / 2
    cy = MARGEN_SUPERIOR + agente.pos[0] * nCS + nCS / 2

    color_agente = RED if modo == "MDP" else BLUE
    pygame.draw.circle(screen, color_agente, (int(cx), int(cy)), 15)

pos_inicial = ra.choice([p for p in aP if p != meta])

agente_mdp = Agente(pos_inicial)
agente_smdp = Agente(pos_inicial)

offset_mdp = 0
offset_smdp = nMapW * nCS + SEPARACION

clock = pygame.time.Clock()

TIEMPO_MDP_MS = 1000
ESCALA_TIEMPO_SMDP_MS = 1000

while not (agente_mdp.termino and agente_smdp.termino):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    tiempo_actual = pygame.time.get_ticks()

    if not agente_mdp.termino and tiempo_actual >= agente_mdp.proximo_movimiento:
        if agente_mdp.pos == meta:
            agente_mdp.termino = True
        else:
            accion_mdp = coord_accion_mdp[agente_mdp.pos]
            agente_mdp.mover(accion_mdp, "MDP")
            agente_mdp.proximo_movimiento = tiempo_actual + TIEMPO_MDP_MS

    if not agente_smdp.termino and tiempo_actual >= agente_smdp.proximo_movimiento:
        if agente_smdp.pos == meta:
            agente_smdp.termino = True
        else:
            accion_smdp = coord_accion_smdp[agente_smdp.pos]
            agente_smdp.mover(accion_smdp, "SMDP")
            agente_smdp.proximo_movimiento = tiempo_actual + int(
                agente_smdp.ultimo_tiempo * ESCALA_TIEMPO_SMDP_MS
            )

    screen.fill(WHITE)

    dibujar_laberinto(offset_mdp, "MDP", coord_accion_mdp, agente_mdp, "MDP")
    dibujar_laberinto(offset_smdp, "SMDP", coord_accion_smdp, agente_smdp, "SMDP")

    pygame.display.flip()
    clock.tick(60)

screen.fill(WHITE)
dibujar_laberinto(offset_mdp, "MDP", coord_accion_mdp, agente_mdp, "MDP")
dibujar_laberinto(offset_smdp, "SMDP", coord_accion_smdp, agente_smdp, "SMDP")
pygame.display.flip()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()