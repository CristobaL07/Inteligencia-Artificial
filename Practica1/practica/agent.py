import enum
import os
import random
from os import waitpid
from queue import PriorityQueue
from time import sleep, time

from joblib.parallel import method

from practica import joc, estat
from practica.estat import Estat
from practica.joc import Accions

class SearchMetodes(enum.Enum):
    """ Enumerdo métodos de busqueda.

    """
    PROFUNDIDAD = 0
    A_STAR = 1
    MINIMAX = 2



class Viatger(joc.Viatger):

    method = SearchMetodes.MINIMAX.value

    def __init__(self, *args, **kwargs):
        super(Viatger, self).__init__(*args, **kwargs)
        self.__proves = [
            (Accions.MOURE, "E"),
            (Accions.MOURE, "S"),
            (Accions.MOURE, "N"),
            (Accions.MOURE, "O"),
            (Accions.BOTAR, "S"),
            (Accions.BOTAR, "N"),
            (Accions.BOTAR, "E"),
            (Accions.BOTAR, "O"),
            (Accions.POSAR_PARET, "S"),
            (Accions.POSAR_PARET, "N"),
            (Accions.POSAR_PARET, "E"),
            (Accions.POSAR_PARET, "O"),

        ]

        self.need_to_visit = []
        self.visited = dict()
        self.__cami_exit = None
        self.count = 0

        match self.method:
            case 0:
                print("PROFUNDIDAD")
            case 1:
                print("A*")
            case 2:
                if self.nom == "Agent 1":
                    print("MINIMAX")

    def pinta(self, display):
        pass

    "PROFUNDIDAD"
    def cerca_profundidad(self, initial_state: estat) -> bool:
        self.need_to_visit = []
        self.visited = set()
        exit = False
        start = time()

        self.need_to_visit.append(initial_state)
        while self.need_to_visit:
            actual = self.need_to_visit.pop()

            if actual in self.visited or not actual.es_segur():
                continue

            if actual.es_meta():
                break

            for f in actual.genera_fill():
                #print(f)
                self.need_to_visit.append(f)

            self.visited.add(actual)

        if actual.es_meta():
            self.__cami_exit = actual.acciones_previas
            exit = True

        print(f"CERRADOS: {len(self.visited)}, ABIERTOS: {len(self.need_to_visit)}")
        end = time()
        print(f"Tiempo de ejecución: {end - start} segundos")
        return exit

    "A*"
    def cerca_A_star(self, initial_state: estat) -> bool:
        self.need_to_visit = PriorityQueue()
        self.visited = set()
        exit = False
        start = time()

        self.need_to_visit.put((initial_state.calc_heuristica(), initial_state))

        actual = None
        while self.need_to_visit:
            h, actual = self.need_to_visit.get()

            if actual in self.visited or not actual.es_segur():
                continue

            if actual.es_meta():
                break

            for f in actual.genera_fill():
                self.need_to_visit.put((f.calc_heuristica(), f))

            self.visited.add(actual)

        if actual.es_meta():
            self.__cami_exit = actual.acciones_previas
            exit = True

        print(f"CERRADOS: {len(self.visited)}, ABIERTOS: {self.need_to_visit.qsize()}")
        end = time()
        print(f"Tiempo de ejecución: {end - start} segundos")
        return exit

    "MINIMAX"

    def cerca_Minimax(self, initial_state: estat, alpha, beta, torn_max=True):
        if initial_state.es_meta():
            self.__cami_exit = initial_state.acciones_previas
            return initial_state, initial_state.calc(self.nom)

        mejor_valor = -float('inf') if torn_max else float('inf')
        mejor_nodo = None
        self.visited[initial_state] = None

        for fill in sorted(initial_state.genera_fills(self.nom), key=lambda x: x.calc(self.nom)):
            self.need_to_visit.append(fill)
            if fill in self.visited or not fill.es_segur():
                continue
            nodo_actual, punt_fill = self.cerca_Minimax(fill, alpha, beta, not torn_max)

            if torn_max and punt_fill > mejor_valor:
                mejor_valor, mejor_nodo = punt_fill, fill
                alpha = max(alpha, punt_fill)
            elif not torn_max and punt_fill < mejor_valor:
                mejor_valor, mejor_nodo = punt_fill, fill
                beta = min(beta, punt_fill)

            if alpha >= beta:
                break

        return mejor_nodo if mejor_nodo else initial_state, mejor_valor if mejor_nodo else 0

    def actua(self, percepcio: dict) -> Accions | tuple[Accions, str]:
        self.count += 1
        estado_inicial = Estat(
                                percepcio["PARETS"],
                                percepcio["TAULELL"],
                                percepcio["DESTI"],
                                percepcio["AGENTS"],
                                0,
            )

        res = None
        if self.nom == "Agent 1":
            agente = True
        else:
            agente = False

        if self.__cami_exit is None:

            match self.method:
                case 0:
                    self.cerca_profundidad(estado_inicial)
                case 1:
                    self.cerca_A_star(estado_inicial)
                case 2:
                    start = time()
                    res = self.cerca_Minimax(estado_inicial, alpha=-float('inf'), beta=float('-inf'), torn_max = agente)
                    end = time()
                    print(f"CERRADOS: {len(self.visited)}, ABIERTOS: {len(self.need_to_visit)}")
                    print(f"Tiempo de ejecución: {end - start} segundos")

        if self.method == 2:
            if isinstance(res, tuple) and res[0] is not None and res[0].acciones_previas is not None and len(res[0].acciones_previas) > 0:
                solucio, punt = res
                aux = solucio.acciones_previas.pop(0)
                acc = aux[1]
                print(aux)
                self.__cami_exit = None
                return acc[0], acc[1]
            else:
                return Accions.ESPERAR
        else:
            if self.__cami_exit:
                aux = self.__cami_exit.pop(0)
                acc = aux[1]
                print(aux)
                return acc[0], acc[1]
            else:
                return Accions.ESPERAR