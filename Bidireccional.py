import time
import psutil  # Para medir el consumo de memoria
from collections import deque, defaultdict
import streamlit as st
from streamlit_flow import streamlit_flow
from streamlit_flow.elements import StreamlitFlowNode, StreamlitFlowEdge

# Variables globales para asignar IDs y almacenar nodos y aristas
node_counter = 0
nodes_data = []
edges_data = []

class Nodo:
    def __init__(self, estado, padre=None, id=None, depth=0, node_type='default'):
        self.estado = estado
        self.padre = padre
        self.id = id  # ID único para visualización
        self.depth = depth
        self.node_type = node_type

def create_node(estado, padre=None, node_type='default'):
    global node_counter
    if padre:
        depth = padre.depth + 1
    else:
        depth = 0
    node = Nodo(estado, padre, id=node_counter, depth=depth, node_type=node_type)
    # Añadir nodo a nodes_data
    node_label = str(estado)
    nodes_data.append({
        'id': str(node.id),
        'label': node_label,
        'depth': depth,
        'node_type': node_type
    })
    node_counter += 1
    return node

def validar_estado(estado):
    o_izq, l_izq, b, o_der, l_der = estado
    if o_izq < 0 or l_izq < 0 or o_der < 0 or l_der < 0:
        return False
    if (o_izq > 0 and o_izq < l_izq) or (o_der > 0 and o_der < l_der):
        return False
    return True

def generar_acciones(estado):
    acciones = []
    o_izq, l_izq, b, o_der, l_der = estado
    movimientos = [(1, 0), (2, 0), (0, 1), (0, 2), (1, 1)]
    for do, dl in movimientos:
        if b == 1:
            nuevo_estado = (o_izq - do, l_izq - dl, 0, o_der + do, l_der + dl)
        else:
            nuevo_estado = (o_izq + do, l_izq + dl, 1, o_der - do, l_der - dl)
        if validar_estado(nuevo_estado):
            acciones.append(nuevo_estado)
    return acciones

def bidireccional(nodo_inicial, nodo_final):
    global edges_data
    frontera_inicial = deque([nodo_inicial])
    frontera_final = deque([nodo_final])
    explorado_inicial = set()
    explorado_final = set()
    nodos_visitados = 0

    padres_inicial = {nodo_inicial.estado: nodo_inicial}
    padres_final = {nodo_final.estado: nodo_final}

    while frontera_inicial and frontera_final:
        # Expandir desde el lado inicial
        nodo_actual_inicial = frontera_inicial.popleft()
        explorado_inicial.add(nodo_actual_inicial.estado)
        nodos_visitados += 1

        acciones = generar_acciones(nodo_actual_inicial.estado)
        for accion in acciones:
            if accion not in explorado_inicial:
                hijo = create_node(accion, padre=nodo_actual_inicial)
                # Añadir arista de padre a hijo
                edges_data.append({
                    'source': str(nodo_actual_inicial.id),
                    'target': str(hijo.id)
                })
                if accion in padres_inicial:
                    continue
                padres_inicial[accion] = hijo
                frontera_inicial.append(hijo)

                if accion in padres_final:
                    # Se encontró una conexión
                    return hijo, padres_final[accion], nodos_visitados

        # Expandir desde el lado final
        nodo_actual_final = frontera_final.popleft()
        explorado_final.add(nodo_actual_final.estado)
        nodos_visitados += 1

        acciones = generar_acciones(nodo_actual_final.estado)
        for accion in acciones:
            if accion not in explorado_final:
                hijo = create_node(accion, padre=nodo_actual_final)
                # Añadir arista de padre a hijo
                edges_data.append({
                    'source': str(nodo_actual_final.id),
                    'target': str(hijo.id)
                })
                if accion in padres_final:
                    continue
                padres_final[accion] = hijo
                frontera_final.append(hijo)

                if accion in padres_inicial:
                    # Se encontró una conexión
                    return padres_inicial[accion], hijo, nodos_visitados

    return None, None, nodos_visitados

def reconstruir_camino(nodo_desde_inicial, nodo_desde_final):
    # Camino desde el inicio hasta el punto de encuentro
    camino_inicial = []
    nodo = nodo_desde_inicial
    while nodo:
        camino_inicial.append(nodo.estado)
        nodo = nodo.padre
    camino_inicial.reverse()

    # Camino desde el punto de encuentro hasta el objetivo
    camino_final = []
    nodo = nodo_desde_final.padre  # Evitar duplicar el estado de encuentro
    while nodo:
        camino_final.append(nodo.estado)
        nodo = nodo.padre

    camino_total = camino_inicial + camino_final
    return camino_total

def assign_positions(nodes_data):
    depth_dict = defaultdict(list)
    for node in nodes_data:
        depth = node['depth']
        depth_dict[depth].append(node)

    for depth, nodes in depth_dict.items():
        y_spacing = 100
        x = depth * 200
        num_nodes = len(nodes)
        total_height = (num_nodes - 1) * y_spacing
        y_start = -total_height / 2
        for i, node in enumerate(nodes):
            y = y_start + i * y_spacing
            node['pos'] = (x, y)
    return nodes_data

def main():
    global nodes_data, edges_data

    # Iniciar el seguimiento de memoria y tiempo
    process = psutil.Process()
    memoria_inicial = process.memory_info().rss / (1024 * 1024)  # Convertir a MB
    inicio_tiempo = time.time()

    estado_inicial = (3, 3, 1, 0, 0)  # (ovejas_izq, lobos_izq, barco, ovejas_der, lobos_der)
    nodo_raiz_inicial = create_node(estado_inicial, node_type='input')

    estado_final = (0, 0, 0, 3, 3)
    nodo_raiz_final = create_node(estado_final, node_type='output')

    solucion_desde_inicial, solucion_desde_final, nodos_visitados = bidireccional(
        nodo_raiz_inicial, nodo_raiz_final)

    # Medir tiempo y memoria después de la ejecución
    fin_tiempo = time.time()
    memoria_final = process.memory_info().rss / (1024 * 1024)  # Convertir a MB

    memoria_consumida = memoria_final - memoria_inicial
    tiempo_ejecucion = (fin_tiempo - inicio_tiempo) * 1000  # Convertir a milisegundos

    if solucion_desde_inicial and solucion_desde_final:
        camino_total = reconstruir_camino(solucion_desde_inicial, solucion_desde_final)
        st.write("### Se encontró una solución:")
        st.write("**Camino:**")
        for idx, estado in enumerate(camino_total):
            o_izq, l_izq, b, o_der, l_der = estado
            lado_barco = 'Izquierda' if b == 1 else 'Derecha'
            st.write(f"Paso {idx + 1}: Ovejas Izq: {o_izq}, Lobos Izq: {l_izq}, Barco: {lado_barco}, Ovejas Der: {o_der}, Lobos Der: {l_der}")

        st.write("\n**Medidas de rendimiento:**")
        st.write(f"- Nodos visitados: {nodos_visitados}")
        st.write(f"- Tiempo de ejecución: {tiempo_ejecucion:.2f} ms")
        st.write(f"- Memoria RAM consumida: {memoria_consumida:.2f} MB")
    else:
        st.write("No se encontró una solución.")

    # Asignar posiciones a los nodos
    nodes_data = assign_positions(nodes_data)

    # Crear objetos StreamlitFlowNode y StreamlitFlowEdge
    nodes = []
    for node_data in nodes_data:
        node_id = node_data['id']
        pos = node_data['pos']
        label = node_data['label']
        node_type = node_data.get('node_type', 'default')
        data = {'content': label}
        node = StreamlitFlowNode(
            id=node_id,
            pos=pos,
            data=data,
            node_type=node_type,
            draggable=False
        )
        nodes.append(node)

    edges = []
    for edge_data in edges_data:
        edge_id = edge_data['source'] + '-' + edge_data['target']
        source = edge_data['source']
        target = edge_data['target']
        edge = StreamlitFlowEdge(edge_id, source, target, animated=True)
        edges.append(edge)

    st.write("### Árbol de búsqueda generado:")
    streamlit_flow(
        'search_tree',
        nodes,
        edges,
        fit_view=True,
        show_minimap=True,
        show_controls=True,
        pan_on_drag=True,
        allow_zoom=True
    )

if __name__ == "__main__":
    main()
