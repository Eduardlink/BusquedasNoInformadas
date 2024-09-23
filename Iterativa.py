import time
import tracemalloc  # Importar tracemalloc para medir memoria
import streamlit as st
from collections import deque
from streamlit_flow import streamlit_flow
from streamlit_flow.elements import StreamlitFlowNode, StreamlitFlowEdge

class Nodo:
    def __init__(self, estado, padre=None, accion=None, id=None):
        self.estado = estado
        self.padre = padre
        self.accion = accion
        self.hijos = []
        self.id = id  # Identificador único para cada nodo

    def agregar_hijo(self, hijo):
        self.hijos.append(hijo)

def validar_estado(estado):
    s_izq, l_izq, b, s_der, l_der = estado
    # Verificar que no haya números negativos
    if s_izq < 0 or l_izq < 0 or s_der < 0 or l_der < 0:
        return False
    # Verificar que las ovejas no sean superadas por lobos en ningún lado
    if (s_izq > 0 and s_izq < l_izq) or (s_der > 0 and s_der < l_der):
        return False
    return True

def generar_acciones(estado):
    acciones = []
    movimientos = [(1, 0), (2, 0), (0, 1), (0, 2), (1, 1)]
    for ds, dl in movimientos:
        acciones.append((ds, dl))
    return acciones

def expandir_nodo(nodo):
    acciones = generar_acciones(nodo.estado)
    for accion in acciones:
        ds, dl = accion
        # Aplicar la acción para obtener el nuevo estado
        if nodo.estado[2] == 1:
            # Barco en la orilla izquierda
            nuevo_estado = (nodo.estado[0] - ds, nodo.estado[1] - dl, 0,
                            nodo.estado[3] + ds, nodo.estado[4] + dl)
        else:
            # Barco en la orilla derecha
            nuevo_estado = (nodo.estado[0] + ds, nodo.estado[1] + dl, 1,
                            nodo.estado[3] - ds, nodo.estado[4] - dl)
        # Crear un nuevo nodo sin validar aún
        nuevo_nodo = Nodo(nuevo_estado, padre=nodo, accion=accion)
        # Verificar si el nuevo estado es válido
        if validar_estado(nuevo_estado):
            nodo.agregar_hijo(nuevo_nodo)
    return nodo.hijos

def get_depth(nodo):
    depth = 0
    while nodo.padre:
        nodo = nodo.padre
        depth +=1
    return depth

def depth_limited_search(nodo_inicial, limit, nodes_list, edges_list, node_positions, level_positions, node_counter):
    frontera = []
    frontera.append((nodo_inicial, 0))  # Nodo y profundidad
    visitados = set()
    nodos_expandidos = 0

    while frontera:
        nodo_actual, depth = frontera.pop()
        nodos_expandidos += 1

        if nodo_actual.estado == (0, 0, 0, 3, 3):
            return nodo_actual, nodos_expandidos, node_counter

        if depth >= limit:
            continue

        if nodo_actual.estado in visitados:
            continue

        visitados.add(nodo_actual.estado)

        hijos = expandir_nodo(nodo_actual)

        if depth + 1 not in level_positions:
            level_positions[depth + 1] = 0

        for hijo in hijos:
            hijo.id = str(node_counter)
            node_counter +=1

            # Asignar posición
            x = (depth + 1) * 200  # Ajustar separación en x según sea necesario
            y = level_positions[depth + 1] * 100  # Ajustar separación en y según sea necesario
            node_positions[hijo.id] = (x, y)
            level_positions[depth + 1] +=1

            # Determinar tipo de nodo
            if hijo.estado == (0, 0, 0, 3, 3):
                node_type = 'output'
            else:
                node_type = 'default'

            # Crear nodo para StreamlitFlow
            nodes_list.append(StreamlitFlowNode(
                id=hijo.id,
                pos=(x, y),
                data={'content': str(hijo.estado)},
                node_type=node_type,
                source_position='right',
                target_position='left',
                draggable=False
            ))

            # Crear arista para StreamlitFlow
            edges_list.append(StreamlitFlowEdge(
                id=f"{nodo_actual.id}-{hijo.id}",
                source=nodo_actual.id,
                target=hijo.id,
                animated=True
            ))

            frontera.append((hijo, depth + 1))

    return None, nodos_expandidos, node_counter

def iddfs_with_visualizacion(nodo_inicial):
    inicio_tiempo = time.time()
    tracemalloc.start()  # Iniciar rastreo de memoria

    nodos_expandidos_total = 0

    # Para visualización
    nodes_list = []
    edges_list = []
    node_positions = {}  # Posiciones de los nodos
    level_positions = {}  # Posiciones en cada nivel
    node_counter = 0  # Contador para asignar IDs únicos

    nodo_inicial.id = str(node_counter)
    node_counter +=1

    # Asignar posición inicial
    node_positions[nodo_inicial.id] = (0, 0)  # x=0 (profundidad), y=0 (orden)
    level_positions[0] = 0  # Inicializar posición y en nivel 0

    # Crear nodo inicial para StreamlitFlow
    nodes_list.append(StreamlitFlowNode(
        id=nodo_inicial.id,
        pos=(0, 0),
        data={'content': str(nodo_inicial.estado)},
        node_type='input',
        source_position='right',
        draggable=False
    ))

    max_depth = 0
    solucion = None

    while True:
        level_positions = {0: 0}  # Reiniciar posiciones por nivel
        result, nodos_expandidos, node_counter = depth_limited_search(
            nodo_inicial, max_depth, nodes_list, edges_list, node_positions, level_positions, node_counter
        )
        nodos_expandidos_total += nodos_expandidos

        if result is not None:
            fin_tiempo = time.time()
            tiempo_ejecucion = (fin_tiempo - inicio_tiempo) * 1000  # Convertir a milisegundos

            # Obtener uso de memoria
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()  # Detener rastreo de memoria
            memoria_consumida = peak  # Memoria máxima en bytes

            return result, nodos_expandidos_total, tiempo_ejecucion, memoria_consumida, nodes_list, edges_list

        max_depth += 1

        # Evitar bucles infinitos
        if max_depth > 20:
            fin_tiempo = time.time()
            tiempo_ejecucion = (fin_tiempo - inicio_tiempo) * 1000  # Convertir a milisegundos

            # Obtener uso de memoria
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()  # Detener rastreo de memoria
            memoria_consumida = peak  # Memoria máxima en bytes

            return None, nodos_expandidos_total, tiempo_ejecucion, memoria_consumida, nodes_list, edges_list

def imprimir_camino(nodo):
    camino = []
    while nodo:
        camino.append(nodo.estado)
        nodo = nodo.padre
    camino.reverse()
    for idx, estado in enumerate(camino):
        s_izq, l_izq, b, s_der, l_der = estado
        st.write(f"Paso {idx + 1}: ({s_izq}, {l_izq}, {b}, {s_der}, {l_der})")

def main():
    st.title("Búsqueda en Profundidad Iterativa  - Ovejas y Lobos")

    estado_inicial = (3, 3, 1, 0, 0)
    nodo_raiz = Nodo(estado_inicial)
    solucion, nodos_expandidos, tiempo_ejecucion, memoria_consumida, nodes_list, edges_list = iddfs_with_visualizacion(nodo_raiz)

    if solucion:
        st.header("Se encontró una solución:")
        imprimir_camino(solucion)
        st.subheader("Medidas de rendimiento:")
        st.write(f"Nodos expandidos: {nodos_expandidos}")
        st.write(f"Tiempo de ejecución: {tiempo_ejecucion:.2f} ms")
        st.write(f"RAM consumida: {memoria_consumida/ 1024:.2f} KB")

        st.header("Árbol de búsqueda generado:")
        # Mostrar el árbol usando streamlit_flow
        streamlit_flow('arbol_busqueda',
                    nodes_list,
                    edges_list,
                    fit_view=True,
                    show_minimap=True,
                    show_controls=True,
                    pan_on_drag=True,
                    allow_zoom=True)
    else:
        st.write("No se encontró una solución.")

if __name__ == "__main__":
    main()
