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

## **¡CÓMO EJECUTAR EL PROGRAMA!**

Para poder probar y ejecutar esta aplicación, por favor, sigue estos sencillos pasos:

1.  **Clonar o Descargar el Repositorio:**
    * Descarga todo el contenido de este repositorio. Puedes usar `git clone https://github.com/sindresorhus/del` o el botón "Code" -> "Download ZIP" en GitHub.
    * Si descargaste un ZIP, descomprímelo en una carpeta de tu elección.

2.  **Instalar Python y `pip`:**
    * Asegúrate de tener **Python 3.x** (preferiblemente Python 3.8 o superior) y `pip` (el gestor de paquetes de Python) instalados en tu sistema. Puedes verificarlo abriendo una terminal (Símbolo del Sistema en Windows, Terminal en macOS/Linux) y escribiendo `python --version` y `pip --version`.

3.  **Instalar las Librerías Necesarias:**
    * Abre tu terminal.
    * Navega hasta la carpeta raíz del proyecto (donde se encuentran `backfinal.py`, `frontfinal.py` y `requirements.txt`). Por ejemplo, si lo descomprimiste en Descargas:
        ```bash
        cd "C:\Users\TuUsuario\Downloads\nombre-de-tu-carpeta-del-proyecto"
        ```
    * Una vez en la carpeta del proyecto, instala todas las librerías necesarias ejecutando:
        ```bash
        pip install -r requirements.txt
        ```

4.  **Iniciar la Aplicación:**
    * **Para Usuarios de Windows (RECOMENDADO):**
        * Simplemente haz **doble clic** en el archivo `iniciar_programa.bat` ubicado en la carpeta raíz del proyecto.
        * Se abrirá una ventana de consola (para el servidor Flask, el backend) y, después de unos segundos, la ventana de la aplicación Tkinter (el frontend).
    * **Para Usuarios de Linux / macOS (Opcional - Si tienes `iniciar_programa.sh`):**
        * Abre una terminal.
        * Navega a la carpeta del proyecto.
        * Primero, dale permisos de ejecución al script: `chmod +x iniciar_programa.sh`
        * Luego, ejecuta el script: `./iniciar_programa.sh`
        * Se iniciará el servidor Flask en segundo plano y luego la aplicación Tkinter.

**¡Puntos Importantes al Ejecutar!**
* **Mantén Abierta la Consola del Backend:** En Windows, la ventana de consola que se abre para el servidor Flask (el backend) **DEBE permanecer abierta** mientras uses la aplicación gráfica. Esta ventana es el "cerebro" que procesa todas las solicitudes de datos y lógica. Si la cierras, la aplicación gráfica dejará de funcionar.
* **Cierre Automático del Backend:** El servidor Flask se intentará cerrar automáticamente cuando cierres la ventana principal de la aplicación Tkinter.

---
el fin
