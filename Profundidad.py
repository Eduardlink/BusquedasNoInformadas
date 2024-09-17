import time
import tracemalloc
import streamlit as st
from streamlit_flow import streamlit_flow
from streamlit_flow.elements import StreamlitFlowNode, StreamlitFlowEdge

class Nodo:
    def __init__(self, estado, padre=None, accion=None, id=None, valido=True):
        self.estado = estado
        self.padre = padre
        self.accion = accion
        self.hijos = []
        self.id = id if id is not None else str(estado)
        self.valido = valido  # Indica si el estado es válido
        self.expanded = False  # Indica si el nodo ya ha sido expandido

    def agregar_hijo(self, hijo):
        self.hijos.append(hijo)

def imprimir_camino(nodo):
    camino = []
    while nodo:
        camino.append(nodo.estado)
        nodo = nodo.padre
    camino.reverse()
    for idx, estado in enumerate(camino):
        st.write(f"Paso {idx + 1}: {estado}")

def validar_estado(estado):
    m_izq, c_izq, b, m_der, c_der = estado
    # Verificar que no haya números negativos
    if m_izq < 0 or c_izq < 0 or m_der < 0 or c_der < 0:
        return False
    # Verificar las reglas del problema
    if (m_izq > 0 and m_izq < c_izq):
        return False
    if (m_der > 0 and m_der < c_der):
        return False
    return True

def generar_acciones():
    # Todas las combinaciones posibles de movimientos
    movimientos = [(1, 0), (2, 0), (0, 1), (0, 2), (1, 1)]
    return movimientos

def expandir_nodo(nodo, nodo_id_counter, visitados):
    acciones = generar_acciones()
    hijos = []
    for accion in acciones:
        dm, dc = accion
        if nodo.estado[2] == 1:  # Barco en la izquierda
            nuevo_estado = (nodo.estado[0] - dm, nodo.estado[1] - dc, 0,
                            nodo.estado[3] + dm, nodo.estado[4] + dc)
        else:  # Barco en la derecha
            nuevo_estado = (nodo.estado[0] + dm, nodo.estado[1] + dc, 1,
                            nodo.estado[3] - dm, nodo.estado[4] - dc)
        # Evaluar si el nuevo estado es válido
        es_valido = validar_estado(nuevo_estado)
        nodo_id_counter[0] += 1
        nuevo_nodo = Nodo(nuevo_estado, padre=nodo, accion=accion, id=str(nodo_id_counter[0]), valido=es_valido)
        nodo.agregar_hijo(nuevo_nodo)
        hijos.append(nuevo_nodo)
    return hijos

def dfs_expand_all(nodo):
    # Iniciar el rastreo de memoria
    tracemalloc.start()

    inicio_tiempo = time.time()
    visitados = set()
    soluciones = []
    nodos_visitados = 0

    # Para visualización con streamlit_flow
    nodes = []
    edges = []
    nodo_id_counter = [0]  # Usamos una lista para poder modificar el contador dentro de funciones

    # Añadir el nodo raíz a la visualización
    nodes.append(StreamlitFlowNode(
        nodo.id,
        (0, 0),
        {'label': str(nodo.estado)}
    ))
    positions = {nodo.id: (0, 0)}  # Guardar posiciones para organizar el árbol

    def dfs_recursivo(nodo, depth=0):
        nonlocal nodos_visitados
        nodos_visitados += 1

        visitados.add(nodo.estado)
        if nodo.estado == (0, 0, 0, 3, 3):
            soluciones.append(nodo)
            return

        hijos = expandir_nodo(nodo, nodo_id_counter, visitados)

        for idx, hijo in enumerate(hijos):
            # Agregar todos los hijos al árbol de visualización, sean válidos o no
            padre_x, padre_y = positions[nodo.id]
            hijo_x = padre_x + 300  # Espacio horizontal entre niveles
            hijo_y = padre_y + (idx - len(hijos) / 2) * 100  # Espacio vertical entre nodos

            positions[hijo.id] = (hijo_x, hijo_y)

            # Definir el color según si el nodo es válido o no
            color = '#A3D3A3' if hijo.valido else '#F7A4A4'  # Verde para válido, rojo para inválido

            # Añadir el nodo hijo a la visualización
            nodes.append(StreamlitFlowNode(
                hijo.id,
                (hijo_x, hijo_y),
                {'label': str(hijo.estado)},
                style={'background': color}
            ))

            # Añadir la arista entre el nodo actual y el hijo
            edges.append(StreamlitFlowEdge(
                f"{nodo.id}-{hijo.id}",
                nodo.id,
                hijo.id,
                label=str(hijo.accion)
            ))

            # Control de nodos repetidos: no expandir si ya se visitó el estado
            if hijo.valido and hijo.estado not in visitados:
                dfs_recursivo(hijo, depth + 1)
            else:
                # Marcar como estéril
                hijo.expanded = True

    dfs_recursivo(nodo)
    fin_tiempo = time.time()
    tiempo_ejecucion = (fin_tiempo - inicio_tiempo) * 1000  # Convertir a milisegundos

    # Obtener el consumo de memoria
    memoria_actual, memoria_pico = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return soluciones, nodos_visitados, tiempo_ejecucion, memoria_pico, nodes, edges

def main():
    st.title("Problema de los Misioneros y Caníbales - Búsqueda en Profundidad")

    estado_inicial = (3, 3, 1, 0, 0)
    nodo_raiz = Nodo(estado_inicial, id='0')
    soluciones, nodos_visitados, tiempo_ejecucion, memoria_pico, nodes, edges = dfs_expand_all(nodo_raiz)

    st.subheader("Árbol de búsqueda generado:")
    # Mostrar el árbol utilizando streamlit_flow
    streamlit_flow(
        'arbol_busqueda',
        nodes,
        edges,
        fit_view=True,
        show_minimap=False,
        show_controls=True,
        pan_on_drag=True,
        allow_zoom=True
    )

    if soluciones:
        st.subheader("Se encontraron las siguientes soluciones:")
        for idx, solucion in enumerate(soluciones):
            st.write(f"**Solución {idx + 1}:**")
            imprimir_camino(solucion)
    else:
        st.write("No se encontraron soluciones.")

    st.subheader("Medidas de rendimiento:")
    st.write(f"- Nodos visitados: {nodos_visitados}")
    st.write(f"- Tiempo de ejecución: {tiempo_ejecucion:.2f} ms")
    st.write(f"- Memoria RAM consumida: {memoria_pico / 1024:.2f} KB")

if __name__ == "__main__":
    main()
