# trabajo-final
Sistema de Gestión de Tienda con Flask y Tkinter

## Descripción del Proyecto

Este proyecto es un **Sistema de Gestión de Tienda** desarrollado en **Python**, combinando un **backend robusto con Flask** y una **interfaz gráfica de usuario (GUI) amigable creada con Tkinter**. Su propósito principal es ofrecer una solución digital eficiente para la administración de pequeñas y medianas tiendas, abordando desafíos comunes como el control manual de inventario y la falta de datos estratégicos.

El sistema permite:
* Gestionar productos (altas, bajas, modificaciones).
* Administrar información de clientes.
* Registrar y consultar el historial de ventas.
* Visualizar estadísticas clave del negocio mediante gráficos interactivos.
* Calcular la utilidad potencial de los productos.

Todo esto se logra a través de una arquitectura **cliente-servidor** que separa claramente la lógica de negocio (Flask) de la presentación (Tkinter), mejorando la modularidad, la escalabilidad y la mantenibilidad del código.

**Principios de POO aplicados:**
* **Clases y Objetos:** Uso de clases como `Producto`, `Persona`, `Venta`, `JsonStorage` en el backend y `TiendaApp` en el frontend, cada una representando una entidad o módulo con su propia lógica.
* **Encapsulamiento:** Los datos y métodos relacionados se agrupan dentro de sus respectivas clases, ocultando la complejidad interna y exponiendo solo lo necesario a través de métodos o la API.
* **Modularidad y Separación de Responsabilidades:** Clara división entre el backend (lógica de negocio y persistencia) y el frontend (interfaz de usuario), comunicándose a través de una API RESTful.

## Enlaces del Proyecto

* **Repositorio de GitHub:** [**Pega aquí el enlace directo a TU REPOSITORIO DE GITHUB**]
    * *Ejemplo: `https://github.com/luismax117/chat/trabajo-final`*
* **Video de Exposición del Proyecto:** [**Pega aquí el enlace directo a TU VIDEO EN YOUTUBE, GOOGLE DRIVE, etc.**]
* **Documentación del Proyecto (PDF):** [**Pega aquí el enlace directo a TU DOCUMENTO PDF en OneDrive o similar**]

## Estructura del Proyecto

El código está organizado siguiendo las buenas prácticas de la **Programación Orientada a Objetos (POO)** y la separación de responsabilidades. Al descargar el repositorio, encontrarás la siguiente estructura:

tu_repositorio_raiz/ (ej. 'trabajo-final')
├── proyecto final de programación/ # CARPETA PRINCIPAL DEL PROGRAMA
│   ├── backfinal.py          # Backend: Servidor Flask con la lógica de negocio y API RESTful.
│   ├── frontfinal.py         # Frontend: Aplicación de interfaz gráfica (GUI) con Tkinter.
│   └── dat/                  # Carpeta para el almacenamiento persistente de datos en formato JSON.
│       ├── product.json      # Almacena datos de productos.
│       ├── person.json       # Almacena datos de clientes/personas.
│       └── venta.json        # Almacena datos de ventas.
└── README.md                 # Este documento (el que estás leyendo en GitHub).

**¡IMPORTANTE!** Asegúrate de que la carpeta de datos se llame **`dat` (en minúsculas)** en tu repositorio de GitHub.

## **¡CÓMO EJECUTAR EL PROGRAMA!**

Para poder probar y ejecutar esta aplicación, por favor, sigue estos sencillos pasos:

1.  **Clonar el Repositorio:**
    * Abre una terminal (o Símbolo del Sistema en Windows, Terminal en macOS/Linux).
    * Navega a la ubicación donde deseas descargar el proyecto (ej. tu carpeta de Documentos).
    * Ejecuta el siguiente comando para clonar el repositorio:
        ```bash
        git clone [https://github.com/luismax117/chat/trabajo-final.git](https://github.com/luismax117/chat/trabajo-final.git)
        ```
    * Luego, ingresa a la carpeta principal del programa:
        ```bash
        cd trabajo-final/proyecto\ final\ de\ programación
        ```
        (Nota: Usa `proyecto\ final\ de\ programación` o `cd "proyecto final de programación"` si el nombre tiene espacios).

2.  **Instalar Python y `pip`:**
    * Asegúrate de tener **Python 3.x** (preferiblemente Python 3.8 o superior) y `pip` (el gestor de paquetes de Python) instalados en tu sistema. Puedes verificarlo escribiendo `python --version` y `pip --version` en la terminal.

3.  **Instalar las Librerías Necesarias:**
    * Desde la carpeta `proyecto final de programación` en tu terminal, instala individualmente las librerías necesarias ejecutando:
        ```bash
        pip install Flask Flask-Cors requests tkcalendar matplotlib
        ```

4.  **Iniciar la Aplicación (Proceso Manual):**
    Una vez que hayas completado los pasos anteriores (clonar, navegar, instalar librerías), la aplicación requiere que el backend (servidor Flask) y el frontend (Tkinter) se inicien por separado.

    * **Paso 4.1: Iniciar el Backend (Servidor Flask)**
        * **Abre una NUEVA terminal** (o Símbolo del Sistema en Windows, o una nueva pestaña/ventana de terminal en Linux/macOS).
        * Navega a la carpeta `proyecto final de programación` en esta nueva terminal:
            ```bash
            cd trabajo-final/proyecto\ final\ de\ programación
            ```
        * Ejecuta el servidor Flask:
            ```bash
            python backfinal.py
            ```
        * **Deja esta terminal abierta y en ejecución.** El servidor Flask se estará ejecutando en segundo plano, escuchando en el puerto 5000.

    * **Paso 4.2: Iniciar el Frontend (Aplicación Tkinter)**
        * Vuelve a la **PRIMERA terminal** que usaste (o abre otra nueva si la cerraste y navega a la carpeta del proyecto).
        * Navega a la carpeta `proyecto final de programación` si aún no estás allí:
            ```bash
            cd trabajo-final/proyecto\ final\ de\ programación
            ```
        * Ejecuta la aplicación Tkinter:
            ```bash
            python frontfinal.py
            ```

**¡Puntos Importantes al Ejecutar!**
* **Dos Terminales Necesarias:** Para que el programa funcione, **debes tener dos ventanas de terminal abiertas simultáneamente**: una ejecutando `python backfinal.py` (el backend) y la otra ejecutando `python frontfinal.py` (el frontend).
* **Mantén Abierta la Terminal del Backend:** La terminal que ejecuta `python backfinal.py` **DEBE permanecer abierta** mientras uses la aplicación gráfica. Esta terminal es el "cerebro" que procesa todas las solicitudes de datos y lógica. Si la cierras, la aplicación gráfica dejará de funcionar.
* **Cierre Manual del Backend:** Cuando termines de usar la aplicación Tkinter y la cierres, deberás volver a la terminal donde iniciaste `python backfinal.py` y cerrarla manualmente (normalmente presionando `Ctrl+C` en la terminal).

---

**ACCIÓN CRÍTICA PARA TI ANTES DE LA ENTREGA:**

1.  **Copia y pega este `README.md` completo** en el `README.md` de la **raíz de tu repositorio** (`luismax117/chat/trabajo-final/README.md`).
2.  **¡MUY IMPORTANTE! Renombra la carpeta de datos a `dat` (en minúsculas) en tu repositorio de GitHub.**

---
el fin
