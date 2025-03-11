import copy
import itertools
from operator import truediv
from pickle import FALSE
from typing import Type

from pygame.display import update

from practica.joc import Viatger, Accions


class Estat:

    def __init__(self, parets: set, tabler: [], desti: tuple[int, int], agents: dict[str, tuple[int, int]], pes: int, cami = None,
    acciones_previas:list[tuple[str, tuple[tuple[Accions,str], tuple[int, int]]]] = None):

        if cami is None:
            cami = []

        if acciones_previas is None:
            acciones_previas = []

        self.parets = parets
        self.tabler = tabler
        self.desti = desti
        self.agents = agents
        self.pes = pes

        self.cami = cami
        self.acciones_previas = acciones_previas

    def __hash__(self):
        return hash((tuple(sorted(self.parets)), self.desti, tuple(sorted(self.agents.items()))))

    def __eq__(self, other):
        return (
                self.parets == other.parets
                and self.desti == other.desti
                and self.agents == other.agents
        )

    def __lt__(self, other):
        return False

    def _legal(self) -> bool:
        """ Mètode per detectar si un estat és legal.

        Un estat és legal si no hi ha cap valor negatiu ni major que el màxim

        Returns:
            Booleà indicant si és legal o no.
        """
        "Si el tablero está vacio, el tablero es ilegal"
        if self.tabler is None:
            return False
        else:
            return True


    def es_meta(self) -> bool:
        """ Mètode per detectar si un estat és META.

        Un estado es meta si el jugador llega a la posicion destino

        Returns:
            Booleà indicant si és META o no.
        """
        for a in self.agents:
            meta = self.agents[a] == self.desti
            if meta:
                return True
        return False

    def es_segur(self) -> bool:
        """ Únicament és segur si hi ha manco llops que gallines, o bé no hi ha gallines.

        Returns:
            Booleà indicant si és segur o no.
        """
        is_Second = False
        b = ""

        if self.desti in self.parets:
            return False

        for a in self.agents:
            if self.agents[a] in self.parets:
                return False

            if is_Second:
                if self.agents[a] == self.agents[b]:
                    return False

            is_Second = not is_Second
            b = a

        return True

    def genera_fill(self) -> list:
        """ Mètode per generar els estats fills.

        Genera tots els estats fill a partir de l'estat actual.

        Returns:
            Llista d'estats fills generats.
        """
        estats_generats = []

        MOVS = {
            "N": (0, -1),
            "O": (-1, 0),
            "S": (0, 1),
            "E": (1, 0),
        }

        "Para cada agente, realizar cada acción"
        for a in self.agents:

            "Poner una paret"
            for direccion in MOVS:
                new_wall = self.poner_pared(a, MOVS[direccion])
                new_walls = copy.deepcopy(self.parets)
                new_walls.add(new_wall)
                "Se crea un nuevo estado"
                new_state = Estat(
                    new_walls,
                    self.update_tabler(self.agents, new_walls),
                    self.desti,
                    self.agents,
                    self.pes + 4,
                    self.cami,
                    self.acciones_previas + [(a, (Accions.POSAR_PARET, direccion), new_wall)]
                )

                "Se comprueba que ese estado sea legal, si SÍ lo es, se añade a la lista de hijos"
                if new_state._legal():
                    # print(f"Added new state PONER_PARET in {direccion} for: {a}")
                    estats_generats.append(new_state)

                "Mover el agente 2 CASILLAS"
                for direccion in MOVS:
                    new_pos_agent = self.mover_agente(a, 2, MOVS[direccion])
                    new_agents = copy.deepcopy(self.agents)
                    new_agents[a] = new_pos_agent

                    "Se crea un nuevo estado"
                    new_state = Estat(
                        self.parets,
                        self.update_tabler(new_agents, self.parets),
                        self.desti,
                        new_agents,
                        self.pes + 2,
                        self.cami,
                        self.acciones_previas + [(a, (Accions.BOTAR, direccion), new_pos_agent)]
                    )

                    "Se comprueba que ese estado sea legal, si SÍ lo es, se añade a la lista de hijos"
                    if new_state._legal():
                        # print(f"Added new state BOTAR 2 in {direccion} for: {a}")
                        estats_generats.append(new_state)

                "Mover el agente 1 CASILLA"
                for direccion in MOVS:
                    new_pos_agent = self.mover_agente(a, 1, MOVS[direccion])
                    new_agents = copy.deepcopy(self.agents)
                    new_agents[a] = new_pos_agent
                    "Se crea un nuevo estado"
                    new_state = Estat(
                        self.parets,
                        self.update_tabler(new_agents, self.parets),
                        self.desti,
                        new_agents,
                        self.pes + 1,
                        self.cami,
                        self.acciones_previas + [(a, (Accions.MOURE, direccion), new_pos_agent)]  # Cambiado aquí

                    )

                    "Se comprueba que ese estado sea legal, si SÍ lo es, se añade a la lista de hijos"
                    if new_state._legal():
                        estats_generats.append(new_state)

        return estats_generats

    def genera_fills(self, agente: str) -> list:
        """ Mètode per generar els estats fills.

        Genera tots els estats fill a partir de l'estat actual.

        Returns:
            Llista d'estats fills generats.
        """
        estats_generats = []

        MOVS = {
            "N": (0, -1),
            "O": (-1, 0),
            "S": (0, 1),
            "E": (1, 0),
        }

        "Para cada agente, realizar cada acción"
        for a in self.agents:

                if a == agente:

                    "Mover el agente 1 CASILLA"
                    for direccion in MOVS:
                        new_pos_agent = self.mover_agente(a, 1, MOVS[direccion])
                        new_agents = copy.deepcopy(self.agents)
                        new_agents[a] = new_pos_agent
                        "Se crea un nuevo estado"
                        new_state = Estat(
                            self.parets,
                            self.update_tabler(new_agents, self.parets),
                            self.desti,
                            new_agents,
                            self.pes + 1,
                            self.cami,
                            self.acciones_previas + [(a, (Accions.MOURE, direccion), new_pos_agent)]  # Cambiado aquí

                        )

                        "Se comprueba que ese estado sea legal, si SÍ lo es, se añade a la lista de hijos"
                        if new_state._legal():
                            # print(f"Added new state MOURE 1 in {direccion} for: {a}")
                            estats_generats.append(new_state)

                    "Mover el agente 2 CASILLAS"
                    for direccion in MOVS:
                        new_pos_agent = self.mover_agente(a, 2, MOVS[direccion])
                        new_agents = copy.deepcopy(self.agents)
                        new_agents[a] = new_pos_agent

                        "Se crea un nuevo estado"
                        new_state = Estat(
                            self.parets,
                            self.update_tabler(new_agents, self.parets),
                            self.desti,
                            new_agents,
                            self.pes + 2,
                            self.cami,
                            self.acciones_previas + [(a, (Accions.BOTAR, direccion), new_pos_agent)]
                        )

                        "Se comprueba que ese estado sea legal, si SÍ lo es, se añade a la lista de hijos"
                        if new_state._legal():
                            # print(f"Added new state BOTAR 2 in {direccion} for: {a}")
                            estats_generats.append(new_state)

                    "Poner una paret"
                    for direccion in MOVS:
                        new_wall = self.poner_pared(a, MOVS[direccion])
                        new_walls = copy.deepcopy(self.parets)
                        new_walls.add(new_wall)
                        "Se crea un nuevo estado"
                        new_state = Estat(
                            new_walls,
                            self.update_tabler(self.agents, new_walls),
                            self.desti,
                            self.agents,
                            self.pes + 4,
                            self.cami,
                            self.acciones_previas + [(a, (Accions.POSAR_PARET, direccion), new_wall)]
                        )

                        "Se comprueba que ese estado sea legal, si SÍ lo es, se añade a la lista de hijos"
                        if new_state._legal():
                            estats_generats.append(new_state)

        return estats_generats

    def update_tabler(self, new_agents: dict[str, tuple[int,int]], new_walls: set) -> []:
        """ Metodo que crea un nuevo tablero.

        Crea un tablero a partir de los agentes y las paredes actualizadas

        Returns:
           Tablero actualizado.
        """
        N = len(self.tabler)
        new_tabler = [[" "] * N for _ in range(N)]

        "Agregar agentes"
        for a in new_agents:
            if self.is_out_of_range(new_agents[a],N):
                return None
            new_tabler[new_agents[a][0]][new_agents[a][1]] = "O"

        "Agregar paredes"
        for w in new_walls:
            if self.is_out_of_range(w, N):
                return None

            new_tabler[w[0]][w[1]] = "O"

        "Agregar destino"
        new_tabler[self.desti[0]][self.desti[1]] = "O"
        return new_tabler

    def is_out_of_range(self, pos: tuple[int,int], N: int) -> bool:

        if (0<= pos[0] < N) and (0<= pos[1] < N):
            return False

        return True

    def mover_agente(self, nombre_agente: str, multiplicidad: int, direccion: tuple[int,int]) -> tuple[int, int]:
        """ Metodo para mover el agente.

            Mueve el agente pasado por parámetro el nº de casillas seleccionado dada una direccion.

            Returns:
               Nueva posicion del agente.
        """

        "Obtenemos posicion actual del agente"
        pos_actual_x = self.agents[nombre_agente][0]
        pos_actual_y = self.agents[nombre_agente][1]

        "Calcular nuevas posiciones"
        pos_new_x = direccion[0] * multiplicidad + pos_actual_x
        pos_new_y = direccion[1] * multiplicidad + pos_actual_y

        return pos_new_x,pos_new_y

    def poner_pared(self, nombre_agente:str, direccion: tuple[int,int]) -> tuple[int,int]:
        """ Metodo para mover el agente.

            Pone una pared en una casilla contigua al agente indicada por la direccion.

            Returns:
               Posicion de la nueva pared.
        """

        "Obtenemos posicion actual del agente"
        pos_actual_x = self.agents[nombre_agente][0]
        pos_actual_y = self.agents[nombre_agente][1]

        "Calcular posicion de la paret"
        pos_new_x = direccion[0] + pos_actual_x
        pos_new_y = direccion[1] + pos_actual_y

        return pos_new_x, pos_new_y


    def calc_heuristica(self):

        heuristica = 0
        "h(n) es la distancia Manhattan al destino"
        for a in self.agents:
            heuristica = abs(self.agents[a][0] - self.desti[0]) + abs(self.agents[a][1] - self.desti[1])
        return heuristica + self.pes

    def calc(self, agente: str):

        heuristica = 0
        "h(n) es la distancia Manhattan al destino"
        if agente == "Agent 1":
            heuristica = abs(self.agents[agente][0] - self.desti[0]) + abs(self.agents[agente][1] - self.desti[1])
        else:
            heuristica = abs(self.agents[agente][0] - self.desti[0]) + abs(self.agents[agente][1] - self.desti[1])
        return heuristica

    def __str__(self):
        return f"Agentes: {self.agents}, Paredes: {self.parets}, Tablero: {self.tabler}, Destino: {self.desti}"

