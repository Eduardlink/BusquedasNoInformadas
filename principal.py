# -*- coding: utf-8 -*-
import streamlit as st
import os

def ejecutar_archivo(codigo):
    # Ejecutar el código Python proporcionado en el archivo
    try:
        exec(codigo, globals())
    except Exception as e:
        st.error(f"Error al ejecutar el archivo: {e}")

def main():
    st.title("Busquedas no informadas")

    # Menú de opciones para seleccionar el tipo de búsqueda
    opcion = st.selectbox("Selecciona un tipo de búsqueda", ["Selecciona...", "Búsqueda en Anchura", "Búsqueda en Profundidad", "Búsqueda en Profundidad Iterativa", "Búsqueda Bidireccional"])

    if opcion != "Selecciona...":
        # Definir los archivos Python correspondientes a cada opción
        archivos = {
            "Búsqueda en Anchura": "Anchura.py",
            "Búsqueda en Profundidad": "Profundidad.py",
            "Búsqueda en Profundidad Iterativa": "Iterativa.py",
            "Búsqueda Bidireccional": "Bidireccional.py",
        }

        archivo_seleccionado = archivos.get(opcion)

        if archivo_seleccionado and os.path.exists(archivo_seleccionado):
            # Leer el contenido del archivo seleccionado especificando UTF-8
            with open(archivo_seleccionado, "r", encoding="utf-8") as file:
                codigo = file.read()

            # Ejecutar el código del archivo
            st.write(f"Ejecutando el archivo: {archivo_seleccionado}")
            ejecutar_archivo(codigo)
        else:
            st.error(f"Archivo para la opción seleccionada no encontrado: {archivo_seleccionado}")

if __name__ == "__main__":
    main()
