import streamlit as st
from streamlit_flow import streamlit_flow
from streamlit_flow.elements import StreamlitFlowNode, StreamlitFlowEdge
import networkx as nx
from collections import deque

# Clase que representa un estado del problema
class Estado:
    def __init__(self, misioneros_izq, canibales_izq, barco_izq):
        self.misioneros_izq = misioneros_izq
        self.canibales_izq = canibales_izq
        self.barco_izq = barco_izq
        self.misioneros_der = 3 - misioneros_izq
        self.canibales_der = 3 - canibales_izq

    def es_valido(self):
        if self.misioneros_izq < 0 or self.misioneros_der < 0 or self.canibales_izq < 0 or self.canibales_der < 0:
            return False
        if (self.misioneros_izq > 0 and self.misioneros_izq < self.canibales_izq):
            return False
        if (self.misioneros_der > 0 and self.misioneros_der < self.canibales_der):
            return False
        return True

    def es_objetivo(self):
        return self.misioneros_izq == 0 and self.canibales_izq == 0 and not self.barco_izq

    def generar_siguientes_estados(self):
        siguientes_estados = []
        movimientos = [(1, 0), (2, 0), (0, 1), (0, 2), (1, 1)]

        for m, c in movimientos:
            if self.barco_izq:
                nuevo_estado = Estado(self.misioneros_izq - m, self.canibales_izq - c, False)
            else:
                nuevo_estado = Estado(self.misioneros_izq + m, self.canibales_izq + c, True)

            if nuevo_estado.es_valido():
                siguientes_estados.append(nuevo_estado)

        return siguientes_estados

    def __repr__(self):
        lado_izq = f"({self.misioneros_izq}M, {self.canibales_izq}C)"
        lado_der = f"({self.misioneros_der}M, {self.canibales_der}C)"
        ubicacion_barco = "Izq" if self.barco_izq else "Der"
        return f"[{lado_izq} | {lado_der} - Bote: {ubicacion_barco}]"

    def __hash__(self):
        return hash((self.misioneros_izq, self.canibales_izq, self.barco_izq))

    def __eq__(self, other):
        return (self.misioneros_izq, self.canibales_izq, self.barco_izq) == (other.misioneros_izq, other.canibales_izq, other.barco_izq)

# Función para resolver el problema y generar el grafo
def resolver_y_generar_grafo():
    estado_inicial = Estado(3, 3, True)
    cola = deque([(estado_inicial, [])])
    visitados = set()
    grafo = nx.DiGraph()  # Crear un grafo dirigido

    while cola:
        estado_actual, camino = cola.popleft()
        estado_hash = (estado_actual.misioneros_izq, estado_actual.canibales_izq, estado_actual.barco_izq)

        if estado_hash in visitados:
            continue
        visitados.add(estado_hash)

        # Añadir nodo al grafo
        if camino:
            grafo.add_edge(repr(camino[-1]), repr(estado_actual))

        if estado_actual.es_objetivo():
            return grafo, camino + [estado_actual]

        # Generar siguientes estados
        for siguiente in estado_actual.generar_siguientes_estados():
            cola.append((siguiente, camino + [estado_actual]))

    return grafo, None

# Generar el grafo y la solución
grafo, solucion = resolver_y_generar_grafo()

# Convertir nodos y aristas para Streamlit Flow
nodes = [
    StreamlitFlowNode(
        id=repr(estado),  # El ID del nodo debe coincidir con cómo se representa en el grafo
        pos=(i * 50, i * 50),  # Ajusta la posición según tus necesidades
        data={'content': repr(estado)},  # Mostrar el estado como contenido del nodo
        node_type='default'
    ) 
    for i, estado in enumerate(grafo.nodes)
]

# Crear las aristas entre nodos utilizando los IDs correctos
edges = [
    StreamlitFlowEdge(
        id=f'{repr(source)}-{repr(target)}', 
        source=repr(source), 
        target=repr(target), 
        animated=True
    ) 
    for source, target in grafo.edges
]

# Título en la aplicación de Streamlit
st.title("Árbol de Estados para el Problema de Caníbales y Misioneros")

# Mostrar la solución encontrada, si existe
if solucion:
    st.write("Solución:")
    for paso in solucion:
        st.write(paso)
else:
    st.write("No se encontró solución.")

# Dibujar el grafo utilizando Streamlit Flow
streamlit_flow(
    'static_flow',
    nodes,
    edges,
    fit_view=True,
    show_minimap=False,
    show_controls=True,
    pan_on_drag=True,
    allow_zoom=True
)
