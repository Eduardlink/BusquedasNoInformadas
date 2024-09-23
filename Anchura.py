import streamlit as st
from streamlit_flow import streamlit_flow
from streamlit_flow.elements import StreamlitFlowNode, StreamlitFlowEdge
from collections import deque
import time
import psutil

class Nodo:
    def __init__(self, estado, padre=None, accion=None, id=None, valido=True):
        self.estado = estado
        self.padre = padre
        self.accion = accion
        self.hijos = []
        self.id = id  # Identificador único para cada nodo
        self.valido = valido  # Indica si el estado es válido o no

    def agregar_hijo(self, hijo):
        self.hijos.append(hijo)

def validar_estado(estado):
    o_izq, l_izq, b, o_der, l_der = estado
    # Verificar que las cantidades no sean negativas o excedan el total
    if o_izq < 0 or l_izq < 0 or o_der < 0 or l_der < 0:
        return False
    if o_izq > 3 or l_izq > 3 or o_der > 3 or l_der > 3:
        return False
    # Verificar la regla de que las ovejas no sean superadas por lobos en ninguna orilla
    if (o_izq > 0 and o_izq < l_izq):
        return False
    if (o_der > 0 and o_der < l_der):
        return False
    return True

def generar_acciones():
    # Genera todas las posibles acciones
    return [(1, 0), (2, 0), (0, 1), (0, 2), (1, 1)]

def expandir_nodo(nodo, node_id_counter, estados_generados):
    acciones = generar_acciones()
    hijos = []
    for accion in acciones:
        do, dl = accion
        if nodo.estado[2] == 1:
            # Barco en el lado izquierdo
            nuevo_estado = (nodo.estado[0] - do, nodo.estado[1] - dl, 0,
                            nodo.estado[3] + do, nodo.estado[4] + dl)
        else:
            # Barco en el lado derecho
            nuevo_estado = (nodo.estado[0] + do, nodo.estado[1] + dl, 1,
                            nodo.estado[3] - do, nodo.estado[4] - dl)
        es_valido = validar_estado(nuevo_estado)
        nuevo_nodo = Nodo(nuevo_estado, padre=nodo, accion=accion, id=node_id_counter, valido=es_valido)
        nodo.agregar_hijo(nuevo_nodo)
        estados_generados.add(nuevo_estado)
        hijos.append(nuevo_nodo)
        node_id_counter += 1
    return hijos, node_id_counter

def bfs(nodo_raiz):
    inicio_tiempo = time.time()
    proceso = psutil.Process()
    memoria_inicial = proceso.memory_info().rss

    frontera = deque([nodo_raiz])
    estados_visitados = set()
    estados_visitados.add(nodo_raiz.estado)
    estados_generados = set()
    estados_generados.add(nodo_raiz.estado)
    nodos_visitados = 1
    node_id_counter = 1  # Comenzamos desde 1 porque la raíz es 0

    all_nodes = [nodo_raiz]
    all_edges = []
    soluciones = []

    while frontera:
        nodo_actual = frontera.popleft()
        hijos, node_id_counter = expandir_nodo(nodo_actual, node_id_counter, estados_generados)
        for hijo in hijos:
            all_nodes.append(hijo)
            all_edges.append((nodo_actual.id, hijo.id))
            if hijo.valido:
                if hijo.estado not in estados_visitados:
                    frontera.append(hijo)
                    estados_visitados.add(hijo.estado)
                    nodos_visitados += 1
                    # Verificar si es estado objetivo
                    if hijo.estado == (0, 0, 0, 3, 3):
                        soluciones.append(hijo)
            else:
                # Nodo inválido, no se agrega a la frontera para expandir
                pass

    fin_tiempo = time.time()
    tiempo_total = (fin_tiempo - inicio_tiempo) * 1000  # Convertir a milisegundos
    memoria_final = proceso.memory_info().rss
    memoria_consumida = (memoria_final - memoria_inicial) / 1024  # Convertir a kilobytes

    return soluciones, nodos_visitados, all_nodes, all_edges, memoria_consumida, tiempo_total

def main():
    st.title("Búsqueda en Anchura - Ovejas y Lobos")

    estado_inicial = (3, 3, 1, 0, 0)
    nodo_raiz = Nodo(estado_inicial, id=0)
    soluciones, nodos_visitados, all_nodes, all_edges, memoria_consumida, tiempo_total = bfs(nodo_raiz)

    if soluciones:
        st.write("## Se encontraron soluciones:")
        # Mostrar todas las rutas de solución
        for idx, solucion in enumerate(soluciones):
            st.write(f"### Solución {idx + 1}:")
            camino = []
            nodo = solucion
            while nodo:
                camino.append(nodo.estado)
                nodo = nodo.padre
            camino.reverse()
            for step_idx, estado in enumerate(camino):
                st.write(f"Paso {step_idx + 1}: {estado}")
            st.write("---")

    else:
        st.write("No se encontraron soluciones.")

    # Crear nodos y aristas para streamlit_flow
    nodes = []
    edges = []
    node_positions = {}  # Para almacenar posiciones (para visualización)
    y_spacing = 100  # Espaciado vertical entre niveles
    x_spacing = 150  # Espaciado horizontal entre nodos

    # Asignar niveles a los nodos basados en BFS
    levels = {}
    queue = deque([(nodo_raiz, 0)])
    while queue:
        nodo_actual, level = queue.popleft()
        if nodo_actual.id not in levels:
            levels[nodo_actual.id] = level
            for hijo in nodo_actual.hijos:
                queue.append((hijo, level + 1))

    # Agrupar nodos por nivel
    level_nodes = {}
    for nodo in all_nodes:
        level = levels.get(nodo.id, 0)
        if level not in level_nodes:
            level_nodes[level] = []
        level_nodes[level].append(nodo)

    # Asignar posiciones a los nodos
    for level in sorted(level_nodes.keys()):
        nodes_in_level = level_nodes[level]
        n = len(nodes_in_level)
        x_start = (n - 1) * (-x_spacing / 2)
        for i, nodo in enumerate(nodes_in_level):
            x_pos = x_start + i * x_spacing
            y_pos = level * y_spacing
            node_positions[nodo.id] = (x_pos, y_pos)
            # Determinar el tipo de nodo
            if nodo.estado == (0, 0, 0, 3, 3):
                node_type = 'output'
            elif not nodo.valido:
                node_type = 'input'  # Marcamos los estados inválidos con un tipo diferente
            else:
                node_type = 'default'
            # Crear StreamlitFlowNode
            node_label = f"{nodo.estado}"
            nodes.append(StreamlitFlowNode(
                id=str(nodo.id),
                pos=(x_pos, y_pos),
                data={'content': node_label},
                node_type=node_type,
                draggable=False
            ))

    # Crear aristas
    for parent_id, child_id in all_edges:
        edges.append(StreamlitFlowEdge(
            id=f"{parent_id}-{child_id}",
            source=str(parent_id),
            target=str(child_id),
            animated=True
        ))

    # Mostrar el flujo
    streamlit_flow('search_tree',
                    nodes,
                    edges,
                    fit_view=True,
                    show_minimap=True,
                    show_controls=True,
                    pan_on_drag=True,
                    allow_zoom=True)

    st.write(f"\n## Medidas de rendimiento:")
    st.write(f"\tNodos visitados (válidos): {nodos_visitados}")
    st.write(f"\tTotal de nodos generados: {len(all_nodes)}")
    st.write(f"\tTiempo total de ejecución: {tiempo_total:.2f} ms")
    st.write(f"\tMemoria RAM total consumida: {memoria_consumida:.2f} KB")

if __name__ == "__main__":
    main()
