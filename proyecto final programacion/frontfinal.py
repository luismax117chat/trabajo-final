import tkinter as tk
from tkinter import ttk, messagebox, Toplevel
import requests
import json
from datetime import datetime
from tkcalendar import DateEntry, Calendar
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import filedialog
import threading # Importar el módulo threading

API_URL = "http://localhost:5000" # URL base de tu API Flask

class TiendaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Gestión de Tienda") # Título de la ventana principal

        # Crear el control de pestañas (Notebook)
        self.tab_control = ttk.Notebook(root)
        
        # Crear las pestañas individuales
        self.tab_productos = ttk.Frame(self.tab_control)
        self.tab_clientes = ttk.Frame(self.tab_control)
        self.tab_ventas = ttk.Frame(self.tab_control)
        self.tab_estadisticas = ttk.Frame(self.tab_control)
        self.tab_utilidad = ttk.Frame(self.tab_control)
        # self.tab_comentarios = ttk.Frame(self.tab_control) # Pestaña de comentarios eliminada

        # Añadir las pestañas al control de pestañas
        self.tab_control.add(self.tab_productos, text='Productos')
        self.tab_control.add(self.tab_clientes, text='Clientes')
        self.tab_control.add(self.tab_ventas, text='Ventas')
        self.tab_control.add(self.tab_estadisticas, text='Estadísticas')
        # self.tab_control.add(self.tab_comentarios, text='Comentarios') # Pestaña de comentarios eliminada
        self.tab_control.add(self.tab_utilidad, text='Utilidad')
        self.tab_control.pack(expand=1, fill='both') # Empaquetar el control de pestañas para que ocupe todo el espacio

        # Botón global para actualizar todos los datos
        btn_actualizar_todo = ttk.Button(root, text="Actualizar Todos los Datos", command=self.actualizar_todos_los_datos)
        btn_actualizar_todo.pack(pady=5)

        # Cargar el contenido de cada pestaña
        self.cargar_tab_productos()
        self.cargar_tab_clientes()
        self.cargar_tab_ventas()
        self.cargar_tab_estadisticas()
        self.setup_tab_utilidad()

        # Cargar todos los datos al iniciar la aplicación para tener una vista inicial
        self.actualizar_todos_los_datos()

    def mostrar_mensaje(self, titulo, mensaje):
        """Muestra un cuadro de diálogo informativo."""
        # Usa root.after para asegurar que el messagebox se ejecuta en el hilo principal de Tkinter
        self.root.after(0, lambda: messagebox.showinfo(titulo, mensaje))

    def mostrar_error(self, titulo, mensaje):
        """Muestra un cuadro de diálogo de error."""
        # Usa root.after para asegurar que el messagebox se ejecuta en el hilo principal de Tkinter
        self.root.after(0, lambda: messagebox.showerror(titulo, mensaje))

    def _make_api_request_threaded(self, method, endpoint, json_data=None, params=None,
                                   success_callback=None, error_callback=None,
                                   success_msg=None, error_title="Error de API"):
        """
        Realiza una solicitud a la API en un hilo separado para no bloquear la interfaz de usuario.
        Los callbacks (funciones a ejecutar tras éxito o error) se ejecutan en el hilo principal de Tkinter.
        """
        def run_request():
            response = None # Inicializar response para manejo de errores
            try:
                url = f"{API_URL}/{endpoint}" # Construir la URL completa de la API
                
                # Realizar la solicitud HTTP según el método especificado
                if method == 'GET':
                    response = requests.get(url, params=params)
                elif method == 'POST':
                    response = requests.post(url, json=json_data)
                elif method == 'PUT':
                    response = requests.put(url, json=json_data)
                elif method == 'DELETE':
                    response = requests.delete(url, json=json_data)
                else:
                    raise ValueError("Método HTTP no soportado por _make_api_request_threaded")

                response.raise_for_status() # Lanza una excepción si el código de estado es 4xx o 5xx

                result_data = response.json() # Obtener la respuesta JSON
                if success_msg:
                    self.mostrar_mensaje("Éxito", success_msg) # Mostrar mensaje de éxito si se proporciona
                if success_callback:
                    self.root.after(0, success_callback, result_data) # Ejecutar callback de éxito en el hilo principal

            except requests.exceptions.HTTPError as http_err:
                # Manejo de errores HTTP (ej. 404 Not Found, 500 Internal Server Error)
                error_msg = "Error desconocido"
                try:
                    if response and response.content:
                        error_data = response.json()
                        error_msg = error_data.get('error', str(http_err))
                    else:
                        error_msg = str(http_err)
                except json.JSONDecodeError:
                    error_msg = f"Error del servidor: {response.text if response else 'No response'}"
                self.mostrar_error(error_title, f"Error HTTP {response.status_code if response else 'N/A'}: {error_msg}")
                if error_callback:
                    self.root.after(0, error_callback, error_msg)
            except requests.exceptions.ConnectionError as conn_err:
                # Manejo de errores de conexión (ej. el servidor no está corriendo)
                self.mostrar_error(error_title, f"Error de conexión: No se pudo conectar al servidor Flask. Asegúrate de que esté corriendo. {conn_err}")
                if error_callback:
                    self.root.after(0, error_callback, str(conn_err))
            except requests.exceptions.Timeout as timeout_err:
                # Manejo de errores de tiempo de espera
                self.mostrar_error(error_title, f"Tiempo de espera agotado: El servidor tardó demasiado en responder. {timeout_err}")
                if error_callback:
                    self.root.after(0, error_callback, str(timeout_err))
            except requests.exceptions.RequestException as req_err:
                # Otros errores generales de solicitud
                self.mostrar_error(error_title, f"Error de solicitud: {req_err}")
                if error_callback:
                    self.root.after(0, error_callback, str(req_err))
            except ValueError as val_err:
                # Errores de validación interna
                self.mostrar_error(error_title, str(val_err))
                if error_callback:
                    self.root.after(0, error_callback, str(val_err))
            except Exception as ex: # Captura cualquier otra excepción inesperada
                self.mostrar_error(error_title, f"Ocurrió un error inesperado: {ex}")
                if error_callback:
                    self.root.after(0, error_callback, str(ex))

        # Iniciar la solicitud en un hilo separado
        thread = threading.Thread(target=run_request)
        thread.daemon = True # Permite que el programa se cierre incluso si el hilo está corriendo
        thread.start()

    def actualizar_todos_los_datos(self):
        """
        Inicia la actualización de todos los datos en las diferentes pestañas.
        Las operaciones de carga se realizan de forma asíncrona mediante hilos.
        """
        self.mostrar_mensaje("Actualizando", "Cargando datos, por favor espere...")

        # Cargar datos para la pestaña de Productos
        self.cargar_lista_productos()
        self.cargar_productos_combo_editar()

        # Cargar datos para la pestaña de Clientes
        self.cargar_lista_clientes()
        self.cargar_clientes_combo_eliminar()

        # Cargar datos para la pestaña de Ventas
        self.cargar_lista_ventas()
        self.cargar_productos_combo_venta()
        self.cargar_clientes_combo_venta()
        self.cargar_ventas_combo_cancelar()

        # Cargar datos para la pestaña de Estadísticas
        self.actualizar_estadisticas_con_filtro()

        # Mostrar mensaje de actualización completa después de un breve retraso
        self.root.after(2000, lambda: self.mostrar_mensaje("Actualización Completa", "Todos los datos y gráficos han sido actualizados."))


    # --- Pestaña de Productos ---
    def cargar_tab_productos(self):
        """Carga los widgets y elementos de la pestaña de Productos."""
        # Campos de entrada para nombre, stock y origen del producto
        lbl_nombre = ttk.Label(self.tab_productos, text="Nombre:")
        lbl_nombre.grid(row=0, column=0, padx=5, pady=5)
        self.entry_nombre_producto = ttk.Entry(self.tab_productos)
        self.entry_nombre_producto.grid(row=0, column=1, padx=5, pady=5)

        lbl_stock = ttk.Label(self.tab_productos, text="Stock:")
        lbl_stock.grid(row=1, column=0, padx=5, pady=5)
        self.entry_stock_producto = ttk.Entry(self.tab_productos)
        self.entry_stock_producto.grid(row=1, column=1, padx=5, pady=5)

        lbl_origen = ttk.Label(self.tab_productos, text="Origen:")
        lbl_origen.grid(row=2, column=0, padx=5, pady=5)
        self.entry_origen_producto = ttk.Entry(self.tab_productos)
        self.entry_origen_producto.grid(row=2, column=1, padx=5, pady=5)

        # Botón para crear un nuevo producto
        btn_crear_producto = ttk.Button(self.tab_productos, text="Crear Producto", command=self.crear_producto)
        btn_crear_producto.grid(row=3, column=0, columnspan=2, padx=5, pady=10)

        # Combobox para seleccionar un producto a editar/eliminar
        lbl_seleccionar_producto = ttk.Label(self.tab_productos, text="Seleccionar Producto:")
        lbl_seleccionar_producto.grid(row=5, column=0, padx=5, pady=5)
        self.combo_productos_editar = ttk.Combobox(self.tab_productos, values=[])
        self.combo_productos_editar.grid(row=5, column=1, padx=5, pady=5)

        # Botones para modificar y eliminar productos
        btn_modificar_producto = ttk.Button(self.tab_productos, text="Modificar Producto", command=self.modificar_producto)
        btn_modificar_producto.grid(row=6, column=0, columnspan=2, padx=5, pady=10)

        btn_eliminar_producto = ttk.Button(self.tab_productos, text="Eliminar Producto", command=self.eliminar_producto)
        btn_eliminar_producto.grid(row=7, column=0, columnspan=2, padx=5, pady=10)

        # Treeview para mostrar la lista de productos
        self.tree_productos = ttk.Treeview(self.tab_productos, columns=("Stock", "Origen"))
        self.tree_productos.heading("#0", text="Nombre")
        self.tree_productos.heading("Stock", text="Stock")
        self.tree_productos.heading("Origen", text="Origen")
        self.tree_productos.column("#0", width=150)
        self.tree_productos.column("Stock", width=80)
        self.tree_productos.column("Origen", width=100)
        self.tree_productos.grid(row=8, column=0, columnspan=2, padx=5, pady=5)

    def cargar_productos_combo_editar(self):
        """Carga los nombres de los productos en el combobox de edición."""
        def _on_success(productos):
            nombres_productos = [producto['nombre'] for producto in productos]
            self.combo_productos_editar['values'] = nombres_productos
        self._make_api_request_threaded('GET', 'productos', success_callback=_on_success)

    def crear_producto(self):
        """Envía una solicitud a la API para crear un nuevo producto."""
        nombre = self.entry_nombre_producto.get()
        stock = self.entry_stock_producto.get()
        origen = self.entry_origen_producto.get()
        if nombre and stock and origen and stock.isdigit():
            payload = {"nombre": nombre, "stock": int(stock), "origen": origen}
            self._make_api_request_threaded('POST', 'productos', json_data=payload,
                                             success_msg=f"Producto '{nombre}' creado exitosamente.",
                                             success_callback=lambda _: self.actualizar_todos_los_datos()) # Actualizar UI tras éxito
            # Limpiar campos después de la creación
            self.entry_nombre_producto.delete(0, tk.END)
            self.entry_stock_producto.delete(0, tk.END)
            self.entry_origen_producto.delete(0, tk.END)
        else:
            self.mostrar_error("Error", "Por favor, complete todos los campos y asegúrese de que el stock sea un número entero válido.")

    def modificar_producto(self):
        """Envía una solicitud a la API para modificar un producto existente."""
        seleccion = self.combo_productos_editar.get()
        nuevo_nombre = self.entry_nombre_producto.get()
        nuevo_stock = self.entry_stock_producto.get()
        nuevo_origen = self.entry_origen_producto.get()

        if seleccion and nuevo_nombre and nuevo_stock and nuevo_origen and nuevo_stock.isdigit():
            payload = {"nombre": nuevo_nombre, "stock": int(nuevo_stock), "origen": nuevo_origen}
            self._make_api_request_threaded('PUT', f'productos/{seleccion}', json_data=payload,
                                             success_msg=f"Producto '{seleccion}' modificado exitosamente.",
                                             success_callback=lambda _: self.actualizar_todos_los_datos()) # Actualizar UI tras éxito
            # Limpiar campos después de la modificación
            self.entry_nombre_producto.delete(0, tk.END)
            self.entry_stock_producto.delete(0, tk.END)
            self.entry_origen_producto.delete(0, tk.END)
        else:
            self.mostrar_error("Error", "Por favor, seleccione un producto e ingrese los nuevos datos válidos (nombre, stock como número y origen).")

    def eliminar_producto(self):
        """Envía una solicitud a la API para eliminar un producto."""
        seleccion = self.combo_productos_editar.get()
        if seleccion:
            if messagebox.askyesno("Confirmar Eliminación", f"¿Seguro que desea eliminar el producto '{seleccion}'? Esta acción es irreversible y también eliminará las ventas asociadas."):
                self._make_api_request_threaded('DELETE', f'productos/{seleccion}',
                                                 success_msg=f"Producto '{seleccion}' eliminado exitosamente.",
                                                 success_callback=lambda _: self.actualizar_todos_los_datos()) # Actualizar UI tras éxito
        else:
            self.mostrar_error("Error", "Por favor, seleccione un producto para eliminar.")

    def cargar_lista_productos(self):
        """Carga y muestra la lista de productos en el Treeview."""
        def _on_success(productos):
            for item in self.tree_productos.get_children(): # Limpiar Treeview existente
                self.tree_productos.delete(item)
            for producto in productos: # Insertar nuevos datos
                self.tree_productos.insert("", tk.END, text=producto['nombre'],
                                           values=(producto['stock'], producto.get('origen', 'N/A')))
        self._make_api_request_threaded('GET', 'productos', success_callback=_on_success)


    ## --- Pestaña de Clientes ---
    def cargar_tab_clientes(self):
        """Carga los widgets y elementos de la pestaña de Clientes."""
        # Campo de entrada para el nombre del cliente
        lbl_nombre = ttk.Label(self.tab_clientes, text="Nombre:")
        lbl_nombre.grid(row=0, column=0, padx=5, pady=5)
        self.entry_nombre_cliente = ttk.Entry(self.tab_clientes)
        self.entry_nombre_cliente.grid(row=0, column=1, padx=5, pady=5)

        # Botón para crear un nuevo cliente
        btn_crear_cliente = ttk.Button(self.tab_clientes, text="Crear Cliente", command=self.crear_cliente)
        btn_crear_cliente.grid(row=1, column=0, columnspan=2, padx=5, pady=10)

        # Combobox para seleccionar un cliente a eliminar
        lbl_seleccionar_cliente_eliminar = ttk.Label(self.tab_clientes, text="Seleccionar Cliente a Eliminar:")
        lbl_seleccionar_cliente_eliminar.grid(row=2, column=0, padx=5, pady=5)
        self.combo_clientes_eliminar = ttk.Combobox(self.tab_clientes, values=[])
        self.combo_clientes_eliminar.grid(row=2, column=1, padx=5, pady=5)

        # Botón para eliminar un cliente
        btn_eliminar_cliente = ttk.Button(self.tab_clientes, text="Eliminar Cliente", command=self.eliminar_cliente)
        btn_eliminar_cliente.grid(row=3, column=0, columnspan=2, padx=5, pady=10)

        # Treeview para mostrar la lista de clientes
        self.tree_clientes = ttk.Treeview(self.tab_clientes, columns=())
        self.tree_clientes.heading("#0", text="Nombre")
        self.tree_clientes.column("#0", width=200)
        self.tree_clientes.grid(row=4, column=0, columnspan=2, padx=5, pady=5)

    def cargar_clientes_combo_eliminar(self):
        """Carga los nombres de los clientes en el combobox de eliminación."""
        def _on_success(personas):
            nombres_clientes = [persona['nombre'] for persona in personas]
            self.combo_clientes_eliminar['values'] = nombres_clientes
        self._make_api_request_threaded('GET', 'personas', success_callback=_on_success)

    def crear_cliente(self):
        """Envía una solicitud a la API para crear un nuevo cliente."""
        nombre = self.entry_nombre_cliente.get()
        if nombre:
            payload = {"nombre": nombre}
            self._make_api_request_threaded('POST', 'personas', json_data=payload,
                                             success_msg=f"Cliente '{nombre}' creado exitosamente.",
                                             success_callback=lambda _: self.actualizar_todos_los_datos()) # Actualizar UI tras éxito
            self.entry_nombre_cliente.delete(0, tk.END) # Limpiar campo
        else:
            self.mostrar_error("Error", "Por favor, ingrese el nombre del cliente.")

    def eliminar_cliente(self):
        """Envía una solicitud a la API para eliminar un cliente."""
        seleccion = self.combo_clientes_eliminar.get()
        if seleccion:
            if messagebox.askyesno("Confirmar Eliminación", f"¿Seguro que desea eliminar al cliente '{seleccion}'? Esto también eliminará las ventas asociadas a este cliente."):
                self._make_api_request_threaded('DELETE', f'personas/{seleccion}',
                                                 success_msg=f"Cliente '{seleccion}' eliminado exitosamente.",
                                                 success_callback=lambda _: self.actualizar_todos_los_datos()) # Actualizar UI tras éxito
        else:
            self.mostrar_error("Error", "Por favor, seleccione un cliente para eliminar.")

    def cargar_lista_clientes(self):
        """Carga y muestra la lista de clientes en el Treeview."""
        def _on_success(personas):
            for item in self.tree_clientes.get_children(): # Limpiar Treeview existente
                self.tree_clientes.delete(item)
            for persona in personas: # Insertar nuevos datos
                self.tree_clientes.insert("", tk.END, text=persona.get('nombre'))
        self._make_api_request_threaded('GET', 'personas', success_callback=_on_success)

    ## --- Pestaña de Ventas ---
    def cargar_tab_ventas(self):
        """Carga los widgets y elementos de la pestaña de Ventas."""
        # Combobox para seleccionar producto y cliente para una nueva venta
        lbl_producto = ttk.Label(self.tab_ventas, text="Producto:")
        lbl_producto.grid(row=0, column=0, padx=5, pady=5)
        self.combo_productos_venta = ttk.Combobox(self.tab_ventas, values=[])
        self.combo_productos_venta.grid(row=0, column=1, padx=5, pady=5)

        lbl_cantidad = ttk.Label(self.tab_ventas, text="Cantidad:")
        lbl_cantidad.grid(row=1, column=0, padx=5, pady=5)
        self.entry_cantidad_venta = ttk.Entry(self.tab_ventas)
        self.entry_cantidad_venta.grid(row=1, column=1, padx=5, pady=5)

        lbl_cliente = ttk.Label(self.tab_ventas, text="Cliente:")
        lbl_cliente.grid(row=2, column=0, padx=5, pady=5)
        self.combo_clientes_venta = ttk.Combobox(self.tab_ventas, values=[])
        self.combo_clientes_venta.grid(row=2, column=1, padx=5, pady=5)

        # Botón para realizar una venta
        btn_realizar_venta = ttk.Button(self.tab_ventas, text="Realizar Venta", command=self.realizar_venta)
        btn_realizar_venta.grid(row=3, column=0, columnspan=2, padx=5, pady=10)

        # Combobox y botones para cancelar o modificar ventas existentes
        lbl_seleccionar_venta = ttk.Label(self.tab_ventas, text="Seleccionar Venta a Cancelar o Modificar:")
        lbl_seleccionar_venta.grid(row=5, column=0, padx=5, pady=5)
        self.combo_ventas_cancelar = ttk.Combobox(self.tab_ventas, values=[])
        self.combo_ventas_cancelar.grid(row=5, column=1, padx=5, pady=5)

        btn_cancelar_venta = ttk.Button(self.tab_ventas, text="Cancelar Venta", command=self.cancelar_venta)
        btn_cancelar_venta.grid(row=6, column=0, columnspan=2, padx=5, pady=5)

        btn_modificar_fecha = ttk.Button(self.tab_ventas, text="Modificar Fecha", command=self.cambiar_fecha_venta)
        btn_modificar_fecha.grid(row=7, column=0, columnspan=2, padx=5, pady=5)

        # Treeview para mostrar la lista de ventas
        self.tree_ventas = ttk.Treeview(self.tab_ventas, columns=("Producto", "Cantidad", "Cliente", "Fecha", "Origen"))
        self.tree_ventas.heading("#0", text="Índice") # Un índice simple para identificar ventas
        self.tree_ventas.heading("Producto", text="Producto")
        self.tree_ventas.heading("Cantidad", text="Cantidad")
        self.tree_ventas.heading("Cliente", text="Cliente")
        self.tree_ventas.heading("Fecha", text="Fecha")
        self.tree_ventas.heading("Origen", text="Origen")
        self.tree_ventas.column("#0", width=50)
        self.tree_ventas.grid(row=8, column=0, columnspan=2, padx=5, pady=5)

    def cargar_productos_combo_venta(self):
        """Carga los nombres de los productos en el combobox para nuevas ventas."""
        def _on_success(productos):
            nombres_productos = [producto['nombre'] for producto in productos]
            self.combo_productos_venta['values'] = nombres_productos
        self._make_api_request_threaded('GET', 'productos', success_callback=_on_success)

    def cargar_clientes_combo_venta(self):
        """Carga los nombres de los clientes en el combobox para nuevas ventas."""
        def _on_success(personas):
            nombres_clientes = [persona['nombre'] for persona in personas]
            self.combo_clientes_venta['values'] = nombres_clientes
        self._make_api_request_threaded('GET', 'personas', success_callback=_on_success)

    def cargar_ventas_combo_cancelar(self):
        """Carga las ventas existentes en el combobox para cancelar/modificar."""
        def _on_success(ventas):
            # Formatear las ventas para mostrarlas de forma legible en el combobox
            self.combo_ventas_cancelar['values'] = [
                f"{venta.get('producto', 'N/A')} - {venta.get('cliente', 'Sin nombre')} - {venta.get('fecha', 'N/A')}"
                for venta in ventas
            ]
            self.combo_ventas_cancelar.ventas_data = ventas # Almacenar datos completos para futuras operaciones
        self._make_api_request_threaded('GET', 'ventas', success_callback=_on_success)

    def realizar_venta(self):
        """Envía una solicitud a la API para registrar una nueva venta."""
        producto = self.combo_productos_venta.get()
        cantidad = self.entry_cantidad_venta.get()
        cliente_nombre = self.combo_clientes_venta.get()

        if producto and cantidad and cantidad.isdigit() and int(cantidad) > 0:
            payload = {"producto": {"nombre": producto}, "cantidad": int(cantidad), "cliente": cliente_nombre}
            self._make_api_request_threaded('POST', 'ventas', json_data=payload,
                                             success_msg="Venta realizada exitosamente.",
                                             success_callback=lambda _: self.actualizar_todos_los_datos()) # Actualizar UI tras éxito
            self.entry_cantidad_venta.delete(0, tk.END) # Limpiar campo de cantidad
        else:
            self.mostrar_error("Error", "Por favor, seleccione un producto, un cliente e ingrese una cantidad válida (número entero positivo).")

    def cancelar_venta(self):
        """Envía una solicitud a la API para cancelar una venta y revertir el stock."""
        seleccion = self.combo_ventas_cancelar.get()
        if not seleccion:
            self.mostrar_error("Error", "Debe seleccionar una venta para cancelar.")
            return

        try:
            # Parsear la selección para obtener los detalles de la venta
            partes = seleccion.split(" - ")
            if len(partes) == 3: # Asegurarse de que el formato sea el esperado
                producto, cliente, fecha = partes
            else:
                self.mostrar_error("Error", "Formato de venta no válido en la selección. Asegúrese de que el producto, cliente y fecha estén presentes.")
                return

        except ValueError:
            self.mostrar_error("Error", "Formato de venta no válido.")
            return

        data = {
            "producto": producto,
            "cliente": cliente,
            "fecha": fecha
        }
        if messagebox.askyesno("Confirmar Cancelación", f"¿Seguro que desea cancelar la venta de '{producto}' a '{cliente}' con fecha '{fecha}'? Esto revertirá el stock."):
            self._make_api_request_threaded('DELETE', 'ventas/cancelar', json_data=data,
                                             success_msg="Venta cancelada y stock revertido correctamente.",
                                             success_callback=lambda _: self.actualizar_todos_los_datos()) # Actualizar UI tras éxito

    def cargar_lista_ventas(self):
        """Carga y muestra la lista de ventas en el Treeview."""
        def _on_success(ventas):
            for item in self.tree_ventas.get_children(): # Limpiar Treeview existente
                self.tree_ventas.delete(item)
            for i, venta in enumerate(ventas): # Insertar nuevos datos
                self.tree_ventas.insert("", tk.END, text=i + 1, values=(venta.get('producto', 'N/A'), venta.get('cantidad', 'N/A'), venta.get('cliente', 'Sin nombre'), venta.get('fecha', 'N/A'), venta.get('origen', 'Desconocido')))
        self._make_api_request_threaded('GET', 'ventas', success_callback=_on_success)

    def cambiar_fecha_venta(self):
        """Abre una ventana para seleccionar una nueva fecha para una venta seleccionada."""
        selected = self.tree_ventas.selection() # Obtener la venta seleccionada en el Treeview
        if not selected:
            self.mostrar_error("Error", "Selecciona una venta para cambiar la fecha.")
            return

        item = self.tree_ventas.item(selected[0]) # Obtener los datos de la venta seleccionada
        venta_data = item['values']
        if not venta_data or len(venta_data) < 4:
            self.mostrar_error("Error", "Venta seleccionada no válida o datos incompletos.")
            return

        producto = venta_data[0]
        cliente = venta_data[2]
        fecha_anterior = venta_data[3]

        # Crear una nueva ventana Toplevel para el calendario
        top = Toplevel(self.root)
        top.title("Seleccionar Nueva Fecha")

        # --- OPCIÓN 1: Usar DateEntry (más fácil y con controles de mes/año) ---
        lbl_nueva_fecha = ttk.Label(top, text="Nueva Fecha:")
        lbl_nueva_fecha.pack(padx=10, pady=5)
        
        # Obtener la fecha actual para inicializar el DateEntry
        try:
            # Intentar parsear la fecha_anterior si existe para inicializar
            current_date = datetime.strptime(fecha_anterior, "%Y-%m-%d").date()
        except ValueError:
            # Si no se puede parsear, usar la fecha de hoy
            current_date = datetime.now().date()

        self.date_entry_nueva_fecha = DateEntry(top, selectmode='day', date_pattern="yyyy-mm-dd",
                                               year=current_date.year, month=current_date.month, day=current_date.day)
        self.date_entry_nueva_fecha.pack(padx=10, pady=10)


        # --- OPCIÓN 2 (si insistes en Calendar, tendrías que añadir botones de navegación):
        # Para que el Calendar tenga navegación, necesitarías implementar botones
        # para avanzar/retroceder mes/año y recalcular la vista del calendario.
        # Esto es más complejo que usar DateEntry.
        # cal = Calendar(top, selectmode='day', date_pattern="yyyy-mm-dd")
        # cal.pack(padx=10, pady=10)


        def confirmar():
            """Función para confirmar la nueva fecha y enviar la solicitud a la API."""
            # Obtener la fecha del DateEntry
            nueva_fecha_obj = self.date_entry_nueva_fecha.get_date()
            nueva_fecha_str = nueva_fecha_obj.strftime("%Y-%m-%d") # Formatear la fecha

            datos = {
                "producto": producto,
                "cliente": cliente,
                "fecha_anterior": fecha_anterior,
                "nueva_fecha": nueva_fecha_str
            }
            self._make_api_request_threaded('PUT', 'ventas/cambiar_fecha', json_data=datos,
                                             success_msg="Fecha modificada correctamente.",
                                             success_callback=lambda _: (top.destroy(), self.actualizar_todos_los_datos())) # Cerrar ventana y actualizar UI

        tk.Button(top, text="Confirmar", command=confirmar).pack(padx=5, pady=5)

        # Centrar la ventana Toplevel (opcional, para mejor UX)
        top.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (top.winfo_width() // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (top.winfo_height() // 2)
        top.geometry(f"+{x}+{y}")
        top.transient(self.root) # Hace que la ventana top sea un popup de root
        top.grab_set() # Bloquea interacción con la ventana principal
        self.root.wait_window(top) # Espera a que la ventana top se cierre

    # --- Pestaña de Estadísticas ---
    def cargar_tab_estadisticas(self):
        """Carga los widgets y elementos de la pestaña de Estadísticas."""
        # Selectores de fecha para filtrar estadísticas
        lbl_fecha_inicio = ttk.Label(self.tab_estadisticas, text="Fecha inicio (YYYY-MM-DD):")
        lbl_fecha_inicio.grid(row=0, column=0, padx=5, pady=5)
        self.fecha_inicio_entry = DateEntry(self.tab_estadisticas, date_pattern="yyyy-mm-dd")
        self.fecha_inicio_entry.grid(row=0, column=1, padx=5, pady=5)

        lbl_fecha_fin = ttk.Label(self.tab_estadisticas, text="Fecha fin (YYYY-MM-DD):")
        lbl_fecha_fin.grid(row=1, column=0, padx=5, pady=5)
        self.fecha_fin_entry = DateEntry(self.tab_estadisticas, date_pattern="yyyy-mm-dd")
        self.fecha_fin_entry.grid(row=1, column=1, padx=5, pady=5)

        # Botón para actualizar las estadísticas con el filtro de fechas
        btn_actualizar = ttk.Button(self.tab_estadisticas, text="Actualizar Estadísticas con Filtro", command=self.actualizar_estadisticas_con_filtro)
        btn_actualizar.grid(row=2, column=0, columnspan=2, padx=5, pady=10)

        # Botones para mostrar diferentes tipos de gráficos estadísticos
        btn_ventas_por_dia = ttk.Button(self.tab_estadisticas, text="Ver Ventas por Día", command=lambda: self.mostrar_ventas_por_dia(
            self.fecha_inicio_entry.get_date().strftime("%Y-%m-%d"),
            self.fecha_fin_entry.get_date().strftime("%Y-%m-%d")
        ))
        btn_ventas_por_dia.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

        btn_productos_mas_vendidos = ttk.Button(self.tab_estadisticas, text="Ver Productos Más Vendidos", command=lambda: self.mostrar_productos_mas_vendidos(
            self.fecha_inicio_entry.get_date().strftime("%Y-%m-%d"),
            self.fecha_fin_entry.get_date().strftime("%Y-%m-%d")
        ))
        btn_productos_mas_vendidos.grid(row=4, column=0, columnspan=2, padx=5, pady=5)

        btn_ventas_por_origen = ttk.Button(self.tab_estadisticas, text="Ver Ventas por Origen", command=lambda: self.mostrar_ventas_por_origen(
            self.fecha_inicio_entry.get_date().strftime("%Y-%m-%d"),
            self.fecha_fin_entry.get_date().strftime("%Y-%m-%d")
        ))
        btn_ventas_por_origen.grid(row=5, column=0, columnspan=2, padx=5, pady=5)

        # Botón para guardar el gráfico actual
        btn_guardar_grafico = ttk.Button(self.tab_estadisticas, text="Guardar Gráfico Actual", command=self.guardar_grafico_actual)
        btn_guardar_grafico.grid(row=6, column=0, columnspan=2, padx=5, pady=10)

        # Configuración del área de visualización de gráficos (Matplotlib)
        self.figure = plt.Figure(figsize=(8, 6), dpi=100)
        self.plot = self.figure.add_subplot(111) # Añadir un subplot a la figura
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.tab_estadisticas) # Crear un canvas de Tkinter para la figura
        self.canvas_widget = self.canvas.get_tk_widget() # Obtener el widget Tkinter del canvas
        self.canvas_widget.grid(row=7, column=0, columnspan=2, padx=5, pady=10, sticky="nsew")
        self.tab_estadisticas.grid_rowconfigure(7, weight=1)
        self.tab_estadisticas.grid_columnconfigure(0, weight=1)
        self.tab_estadisticas.grid_columnconfigure(1, weight=1)

    def actualizar_estadisticas_con_filtro(self):
        """
        Obtiene las fechas de inicio y fin de los DateEntry y actualiza
        todos los gráficos estadísticos con esos filtros.
        """
        fecha_inicio = self.fecha_inicio_entry.get_date().strftime("%Y-%m-%d")
        fecha_fin = self.fecha_fin_entry.get_date().strftime("%Y-%m-%d")

        # Llamar a las funciones de mostrar gráficos con los filtros de fecha
        self.mostrar_ventas_por_dia(fecha_inicio, fecha_fin)
        self.mostrar_productos_mas_vendidos(fecha_inicio, fecha_fin)
        self.mostrar_ventas_por_origen(fecha_inicio, fecha_fin)

    def mostrar_grafico(self, data, title, xlabel, ylabel):
        """
        Genera y muestra un gráfico de barras utilizando Matplotlib.
        :param data: Diccionario con los datos del gráfico (keys son etiquetas, values son alturas de barra).
        :param title: Título del gráfico.
        :param xlabel: Etiqueta del eje X.
        :param ylabel: Etiqueta del eje Y.
        """
        self.plot.clear() # Limpiar el plot anterior
        if data:
            labels = list(data.keys())
            values = list(data.values())
            self.plot.bar(labels, values) # Crear el gráfico de barras
            self.plot.set_title(title)
            self.plot.set_xlabel(xlabel)
            self.plot.set_ylabel(ylabel)
            self.figure.tight_layout() # Ajustar el diseño para que todo quepa
        else:
            self.plot.text(0.5, 0.5, 'No hay datos disponibles para mostrar.', ha='center', va='center', transform=self.plot.transAxes)
        self.canvas.draw() # Dibujar el gráfico en el canvas de Tkinter

    def mostrar_ventas_por_dia(self, fecha_inicio=None, fecha_fin=None):
        """Obtiene datos de ventas por día de la API y los muestra en un gráfico."""
        def _on_success(data):
            title = "Ventas por Día"
            if fecha_inicio and fecha_fin:
                title += f" ({fecha_inicio} a {fecha_fin})" # Añadir el rango de fechas al título
            self.mostrar_grafico(data, title, "Día", "Cantidad Vendida")

        params = {}
        if fecha_inicio and fecha_fin:
            params = {"fecha_inicio": fecha_inicio, "fecha_fin": fecha_fin}
        self._make_api_request_threaded('GET', 'estadisticas/ventas_por_dia', params=params, success_callback=_on_success)

    def mostrar_productos_mas_vendidos(self, fecha_inicio=None, fecha_fin=None):
        """Obtiene datos de productos más vendidos de la API y los muestra en un gráfico."""
        def _on_success(data):
            title = "Productos Más Vendidos"
            if fecha_inicio and fecha_fin:
                title += f" ({fecha_inicio} a {fecha_fin})"
            self.mostrar_grafico(data, title, "Producto", "Cantidad Total Vendida")

        params = {}
        if fecha_inicio and fecha_fin:
            params = {"fecha_inicio": fecha_inicio, "fecha_fin": fecha_fin}
        self._make_api_request_threaded('GET', 'estadisticas/productos_mas_vendidos', params=params, success_callback=_on_success)

    def mostrar_ventas_por_origen(self, fecha_inicio=None, fecha_fin=None):
        """Obtiene datos de ventas por origen de la API y los muestra en un gráfico."""
        def _on_success(data):
            title = "Ventas por Origen"
            if fecha_inicio and fecha_fin:
                title += f" ({fecha_inicio} a {fecha_fin})"
            self.mostrar_grafico(data, title, "Origen", "Cantidad Total Vendida")

        params = {}
        if fecha_inicio and fecha_fin:
            params = {"fecha_inicio": fecha_inicio, "fecha_fin": fecha_fin}
        self._make_api_request_threaded('GET', 'estadisticas/ventas_por_origen', params=params, success_callback=_on_success)

    def guardar_grafico_actual(self):
        """Permite al usuario guardar el gráfico actualmente visible como una imagen."""
        # Verificar si hay un gráfico con datos para guardar
        if not self.figure.get_axes() or not self.plot.has_data():
            self.mostrar_error("Error al guardar", "No hay ningún gráfico con datos para guardar. Genere uno primero.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".png", # Extensión por defecto
            filetypes=[("Archivos PNG", "*.png"), # Tipos de archivo permitidos
                       ("Archivos JPEG", "*.jpg"),
                       ("Archivos PDF", "*.pdf"),
                       ("Todos los archivos", "*.*")]
        )

        if file_path:
            try:
                self.figure.savefig(file_path) # Guardar la figura
                self.mostrar_mensaje("Gráfico Guardado", f"El gráfico se guardó en:\n{file_path}")
            except Exception as e:
                self.mostrar_error("Error al guardar gráfico", f"No se pudo guardar el gráfico: {e}")

    # --- NUEVA Pestaña de Utilidad (Cálculo Rápido) ---
    # --- NUEVA Pestaña de Utilidad (Cálculo Rápido) ---
    def setup_tab_utilidad(self):
        """
        Configura la interfaz de usuario para la pestaña de cálculo rápido de utilidad.
        Permite al usuario ingresar el nombre de un producto, su costo de compra,
        el precio de venta y la cantidad vendida para calcular la utilidad total
        de forma inmediata. También muestra una gráfica de las utilidades de los productos calculados.
        """
        input_frame = ttk.LabelFrame(self.tab_utilidad, text="Cálculo Rápido de Utilidad")
        input_frame.pack(padx=10, pady=10, fill="x")

        # Etiqueta y campo de entrada para el nombre del producto
        lbl_producto_utilidad = ttk.Label(input_frame, text="Nombre del Producto:")
        lbl_producto_utilidad.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entry_producto_utilidad = ttk.Entry(input_frame)
        self.entry_producto_utilidad.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # Etiqueta y campo de entrada para el costo (lo que nos costó)
        lbl_costo_compra = ttk.Label(input_frame, text="Costo de Compra (por unidad):")
        lbl_costo_compra.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.entry_costo_compra = ttk.Entry(input_frame)
        self.entry_costo_compra.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        # Etiqueta y campo de entrada para el precio de venta (cómo lo vendimos)
        lbl_precio_venta_utilidad = ttk.Label(input_frame, text="Precio de Venta (por unidad):")
        lbl_precio_venta_utilidad.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.entry_precio_venta_utilidad = ttk.Entry(input_frame)
        self.entry_precio_venta_utilidad.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        # NUEVO: Etiqueta y campo de entrada para la cantidad vendida
        lbl_cantidad_vendida_utilidad = ttk.Label(input_frame, text="Cantidad Vendida:")
        lbl_cantidad_vendida_utilidad.grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.entry_cantidad_vendida_utilidad = ttk.Entry(input_frame)
        self.entry_cantidad_vendida_utilidad.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

        # Configurar la columna 1 para que se expanda y los campos de entrada ocupen el espacio disponible
        input_frame.grid_columnconfigure(1, weight=1)

        # Frame para los botones (cambiada la fila de grid a 4)
        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)

        # Botón para calcular la utilidad
        ttk.Button(button_frame, text="Calcular Utilidad Total", command=self.calcular_utilidad_rapida).pack(side="left", padx=5)
        # Botón para limpiar los campos
        ttk.Button(button_frame, text="Limpiar Campos", command=self.limpiar_campos_utilidad).pack(side="left", padx=5)

        # Etiqueta para mostrar el resultado de la utilidad calculada (cambiada la fila de grid a 5)
        self.lbl_resultado_utilidad = ttk.Label(input_frame, text="Utilidad Total Calculada: N/A", font=("Arial", 12, "bold"))
        self.lbl_resultado_utilidad.grid(row=5, column=0, columnspan=2, pady=10)

        # Frame y configuración para la gráfica de utilidad
        self.utilidad_chart_frame = ttk.Frame(self.tab_utilidad)
        self.utilidad_chart_frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Crear una figura y un eje para el gráfico de utilidad
        self.utilidad_figure, self.utilidad_ax = plt.subplots(figsize=(6, 4), dpi=100)
        # Crear un lienzo (canvas) de Matplotlib para Tkinter
        self.utilidad_canvas = FigureCanvasTkAgg(self.utilidad_figure, master=self.utilidad_chart_frame)
        # Obtener el widget de Tkinter del lienzo
        self.utilidad_plot_widget = self.utilidad_canvas.get_tk_widget()
        # Empaquetar el widget del gráfico en el frame
        self.utilidad_plot_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # Diccionario para almacenar {producto: utilidad total} para el gráfico
        self.productos_utilidad_calculadora = {} 
        # Inicializar el gráfico vacío al inicio
        self.actualizar_grafico_utilidad_calculadora() 

    def limpiar_campos_utilidad(self):
        """
        Limpia los campos de entrada y la etiqueta de resultado en la pestaña de utilidad rápida.
        """
        self.entry_producto_utilidad.delete(0, tk.END)
        self.entry_costo_compra.delete(0, tk.END)
        self.entry_precio_venta_utilidad.delete(0, tk.END)
        self.entry_cantidad_vendida_utilidad.delete(0, tk.END) # NUEVO: Limpiar campo de cantidad
        self.lbl_resultado_utilidad.config(text="Utilidad Total Calculada: N/A")
        self.entry_producto_utilidad.focus_set() # Pone el foco en el primer campo

    def calcular_utilidad_rapida(self):
        """
        Calcula la utilidad total de un producto basándose en el costo de compra, el precio de venta
        y la cantidad vendida, ingresados por el usuario en la calculadora rápida.
        Actualiza la etiqueta de resultado y el gráfico de utilidad.
        """
        producto = self.entry_producto_utilidad.get().strip() # .strip() para eliminar espacios en blanco
        costo_compra_str = self.entry_costo_compra.get().strip()
        precio_venta_str = self.entry_precio_venta_utilidad.get().strip()
        cantidad_vendida_str = self.entry_cantidad_vendida_utilidad.get().strip() # NUEVO: Obtener cantidad

        # Validar que todos los campos estén llenos
        if not all([producto, costo_compra_str, precio_venta_str, cantidad_vendida_str]): # NUEVO: Validar cantidad
            self.mostrar_error("Error", "Todos los campos (Nombre del Producto, Costo de Compra, Precio de Venta, Cantidad Vendida) son obligatorios.")
            return

        try:
            # Intentar convertir los valores a números flotantes
            costo_compra = float(costo_compra_str)
            precio_venta = float(precio_venta_str)
            cantidad_vendida = int(cantidad_vendida_str) # NUEVO: Convertir cantidad a entero
        except ValueError:
            # Mostrar error si la conversión falla
            self.mostrar_error("Error", "Costo de Compra, Precio de Venta y Cantidad Vendida deben ser números válidos.")
            return
        
        # Validar que los precios y la cantidad no sean negativos
        if costo_compra < 0 or precio_venta < 0:
            self.mostrar_error("Error", "Los precios no pueden ser negativos.")
            return
        if cantidad_vendida <= 0: # La cantidad debe ser positiva para calcular utilidad
            self.mostrar_error("Error", "La cantidad vendida debe ser un número entero positivo.")
            return

        # Calcular la utilidad por unidad
        utilidad_por_unidad = precio_venta - costo_compra
        # Calcular la utilidad total
        utilidad_total = utilidad_por_unidad * cantidad_vendida # NUEVO CÁLCULO

        # Actualizar la etiqueta de resultado con la utilidad total calculada
        self.lbl_resultado_utilidad.config(text=f"Utilidad Total Calculada: ${utilidad_total:.2f}")

        # Almacenar o actualizar la utilidad total para el gráfico de la calculadora.
        self.productos_utilidad_calculadora[producto] = utilidad_total
        # Actualizar el gráfico para reflejar los nuevos datos
        self.actualizar_grafico_utilidad_calculadora()

    def actualizar_grafico_utilidad_calculadora(self):
        """
        Actualiza el gráfico de barras que muestra la utilidad total por producto
        calculada en la pestaña de utilidad rápida.
        Las barras son verdes para utilidades positivas (ganancia) y rojas para utilidades negativas (pérdida).
        """
        self.utilidad_ax.clear() # Limpiar el eje del gráfico para dibujar uno nuevo
        
        # Si no hay productos en el diccionario de la calculadora, mostrar un mensaje en el gráfico
        if not self.productos_utilidad_calculadora:
            self.utilidad_ax.text(0.5, 0.5, 'Ingrese datos para ver la utilidad.', 
                                 horizontalalignment='center', verticalalignment='center', transform=self.utilidad_ax.transAxes)
            self.utilidad_canvas.draw_idle() # Redibujar el canvas
            return

        # Obtener la lista de productos y sus utilidades totales del diccionario de la calculadora
        productos = list(self.productos_utilidad_calculadora.keys())
        utilidades = list(self.productos_utilidad_calculadora.values())

        # Definir colores para las barras: rojo para pérdida, verde para ganancia
        colors = ['red' if u < 0 else 'green' for u in utilidades]

        # Crear el gráfico de barras
        self.utilidad_ax.bar(productos, utilidades, color=colors)
        self.utilidad_ax.set_ylabel("Utilidad Total ($)") # Etiqueta del eje Y
        self.utilidad_ax.set_title("Utilidad Total por Producto (Calculadora Rápida)") # Título del gráfico
        self.utilidad_ax.tick_params(axis='x', rotation=45) # Rotar etiquetas del eje X para mejor visibilidad y alinearlas a la derecha
        self.utilidad_ax.grid(axis='y', linestyle='--', alpha=0.7) # Añadir una cuadrícula en el eje Y
        self.utilidad_figure.tight_layout() # Ajustar el diseño para que todo quepa bien
        self.utilidad_canvas.draw_idle() # Redibujar el canvas para mostrar los cambios

if __name__ == "__main__":
    root = tk.Tk() # Inicializar la ventana principal de Tkinter
    app = TiendaApp(root) # Crear una instancia de la aplicación
    root.mainloop() # Iniciar el bucle principal de Tkinter