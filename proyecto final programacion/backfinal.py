from flask import Flask, request, jsonify
import json
import os
from datetime import datetime
from flask_cors import CORS

# Inicializa la aplicación Flask
app = Flask(__name__)
CORS(app)

# Define la ruta base del proyecto para asegurar que los archivos JSON se encuentren
RUTA_BASE = os.path.dirname(os.path.abspath(__file__))

# Define las rutas completas a los archivos JSON dentro de la carpeta 'dat'.
PRODUCTOS_FILE = os.path.join(RUTA_BASE, 'dat', 'product.json')
PERSONAS_FILE = os.path.join(RUTA_BASE, 'dat', 'person.json')
VENTAS_FILE = os.path.join(RUTA_BASE, 'dat', 'venta.json')


# --- UTILIDADES DE ARCHIVO JSON ---
class JsonStorage:
    """
    Clase de utilidad para cargar y guardar datos en archivos JSON.
    Gestiona la existencia del archivo y el manejo de errores básicos.
    """
    def __init__(self, filepath):
        self.filepath = filepath

    def cargar(self):
        """
        Carga los datos de un archivo JSON.
        Retorna una lista vacía si el archivo no existe o está vacío/corrupto,
        lo que permite que la aplicación inicie sin datos iniciales.
        """
        if not os.path.exists(self.filepath):
            return []
        try:
            with open(self.filepath, 'r', encoding='utf-8') as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def guardar(self, datos):
        """
        Guarda los datos en un archivo JSON.
        Crea el directorio si no existe.
        Retorna True si la operación fue exitosa, False en caso de error de E/S.
        :param datos: Los datos (generalmente una lista de diccionarios) a guardar.
        """
        try:
            os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
            with open(self.filepath, 'w', encoding='utf-8') as file:
                json.dump(datos, file, indent=4, ensure_ascii=False)
            return True
        except IOError:
            return False


# --- MODELOS DE DATOS ---

class Producto:
    """
    Clase que representa y gestiona las operaciones CRUD (Crear, Leer, Actualizar, Eliminar)
    para los productos. Interactúa con el almacenamiento JSON a través de JsonStorage.
    """
    storage = JsonStorage(PRODUCTOS_FILE)

    @classmethod
    def todos(cls):
        """
        Retorna una lista de todos los productos almacenados.
        """
        return cls.storage.cargar()

    @classmethod
    def buscar(cls, nombre):
        """
        Busca un producto por su nombre.
        :param nombre: El nombre del producto a buscar.
        :return: El diccionario del producto si se encuentra, de lo contrario None.
        """
        return next((p for p in cls.todos() if p.get('nombre') == nombre), None)

    @classmethod
    def crear(cls, datos):
        """
        Crea un nuevo producto y lo guarda en el almacenamiento.
        Realiza validaciones básicas sobre los datos proporcionados.
        :param datos: Un diccionario con 'nombre', 'stock' y 'origen' del producto.
        :return: Una tupla (datos_del_producto_o_error, código_HTTP).
        """
        if not isinstance(datos, dict) or not all(key in datos for key in ['nombre', 'stock', 'origen']):
            return {'error': 'Datos inválidos: nombre (str), stock (int), y origen (str) son requeridos'}, 400
        if not isinstance(datos['nombre'], str) or not isinstance(datos['stock'], int) or not isinstance(datos['origen'], str):
            return {'error': 'Datos inválidos: nombre (str), stock (int), y origen (str) son requeridos'}, 400
        
        productos = cls.todos()
        if cls.buscar(datos['nombre']):
            return {'error': f'El producto "{datos["nombre"]}" ya existe'}, 409

        productos.append(datos)
        if cls.storage.guardar(productos):
            return datos, 201
        return {'error': 'No se pudo guardar el producto'}, 500

    @classmethod
    def actualizar(cls, nombre, nuevos_datos):
        """
        Actualiza los datos de un producto existente identificado por su nombre.
        :param nombre: El nombre del producto a actualizar.
        :param nuevos_datos: Un diccionario con los campos a actualizar del producto.
        :return: Una tupla (datos_del_producto_actualizado_o_error, código_HTTP).
        """
        productos = cls.todos()
        encontrado = False
        for p in productos:
            if p.get('nombre') == nombre:
                p.update(nuevos_datos)
                encontrado = True
                break
        if encontrado and cls.storage.guardar(productos):
            return p, 200
        return {'error': f'Producto "{nombre}" no encontrado'}, 404

    @classmethod
    def eliminar(cls, nombre):
        """
        Elimina un producto del almacenamiento por su nombre.
        :param nombre: El nombre del producto a eliminar.
        :return: Una tupla (mensaje_o_error, código_HTTP).
        """
        productos = cls.todos()
        nuevos = [p for p in productos if p.get('nombre') != nombre]
        if len(nuevos) < len(productos):
            if cls.storage.guardar(nuevos):
                return {'mensaje': f'Producto "{nombre}" eliminado'}, 200
            return {'error': 'No se pudo eliminar el producto'}, 500
        return {'error': f'Producto "{nombre}" no encontrado'}, 404


class Persona:
    """
    Clase que representa y gestiona las operaciones CRUD para las personas (clientes/empleados).
    Interactúa con el almacenamiento JSON a través de JsonStorage.
    """
    storage = JsonStorage(PERSONAS_FILE)

    @classmethod
    def todos(cls):
        """
        Retorna una lista de todas las personas almacenadas.
        """
        return cls.storage.cargar()

    @classmethod
    def buscar(cls, nombre):
        """
        Busca una persona por su nombre.
        :param nombre: El nombre de la persona a buscar.
        :return: El diccionario de la persona si se encuentra, de lo contrario None.
        """
        return next((p for p in cls.todos() if p.get('nombre') == nombre), None)

    @classmethod
    def crear(cls, datos):
        """
        Crea una nueva persona y la guarda en el almacenamiento.
        Realiza validaciones básicas sobre los datos proporcionados.
        :param datos: Un diccionario con al menos el 'nombre' de la persona.
        :return: Una tupla (datos_de_la_persona_o_error, código_HTTP).
        """
        if not isinstance(datos, dict) or not datos.get('nombre'):
            return {'error': 'Datos inválidos: el nombre es requerido'}, 400
        if not isinstance(datos['nombre'], str):
            return {'error': 'Datos inválidos: el nombre debe ser una cadena'}, 400

        personas = cls.todos()
        if cls.buscar(datos['nombre']):
            return {'error': f'La persona "{datos["nombre"]}" ya existe'}, 409

        personas.append(datos)
        if cls.storage.guardar(personas):
            return datos, 201
        return {'error': 'No se pudo guardar la persona'}, 500

    @classmethod
    def actualizar(cls, nombre, nuevos_datos):
        """
        Actualiza los datos de una persona existente identificada por su nombre.
        :param nombre: El nombre de la persona a actualizar.
        :param nuevos_datos: Un diccionario con los campos a actualizar de la persona.
        :return: Una tupla (datos_de_la_persona_actualizada_o_error, código_HTTP).
        """
        personas = cls.todos()
        encontrado = False
        for p in personas:
            if p.get('nombre') == nombre:
                p.update(nuevos_datos)
                encontrado = True
                break
        if encontrado and cls.storage.guardar(personas):
            return p, 200
        return {'error': f'Persona "{nombre}" no encontrada'}, 404

    @classmethod
    def eliminar(cls, nombre):
        """
        Elimina una persona del almacenamiento por su nombre.
        :param nombre: El nombre de la persona a eliminar.
        :return: Una tupla (mensaje_o_error, código_HTTP).
        """
        personas = cls.todos()
        nuevas = [p for p in personas if p.get('nombre') != nombre]
        if len(nuevas) < len(personas):
            if cls.storage.guardar(nuevas):
                return {'mensaje': f'Persona "{nombre}" eliminada'}, 200
            return {'error': 'No se pudo eliminar la persona'}, 500
        return {'error': f'Persona "{nombre}" no encontrada'}, 404


class Venta:
    """
    Clase que gestiona las operaciones relacionadas con las ventas.
    Además de registrar ventas, se encarga de actualizar el stock de los productos.
    """
    storage = JsonStorage(VENTAS_FILE)

    @classmethod
    def todas(cls):
        """
        Retorna una lista de todas las ventas registradas.
        """
        return cls.storage.cargar()

    @classmethod
    def crear(cls, datos):
        """
        Registra una nueva venta y actualiza el stock del producto vendido.
        :param datos: Un diccionario con 'producto' (dict con 'nombre') y 'cantidad',
                      y opcionalmente 'cliente'.
        :return: Una tupla (datos_de_la_venta_o_error, código_HTTP).
        """
        if not isinstance(datos, dict) or not isinstance(datos.get('producto'), dict) or not isinstance(datos.get('cantidad'), int):
            return {'error': 'Datos inválidos: requiere producto (dict con nombre) y cantidad (int)'}, 400

        nombre_producto = datos['producto'].get('nombre')
        cantidad = datos['cantidad']
        cliente = datos.get('cliente', 'Sin nombre')
        fecha = datetime.now().strftime('%Y-%m-%d')

        if not isinstance(nombre_producto, str) or cantidad <= 0:
            return {'error': 'Datos inválidos: nombre del producto (str) y cantidad (> 0) son requeridos'}, 400

        producto = next((p for p in Producto.todos() if p.get('nombre') == nombre_producto), None)

        if not producto:
            return {'error': f'Producto "{nombre_producto}" no encontrado'}, 404

        if not isinstance(producto.get('stock'), int) or producto['stock'] < cantidad:
            return {'error': f'Stock insuficiente para "{nombre_producto}"'}, 400

        producto['stock'] -= cantidad
        resultado_actualizacion_producto, codigo_actualizacion_producto = Producto.actualizar(nombre_producto, producto)

        if codigo_actualizacion_producto != 200:
            return {'error': f'No se pudo actualizar el stock del producto: {resultado_actualizacion_producto.get("error")}'}, 500

        nueva_venta = {
            'producto': nombre_producto,
            'cantidad': cantidad,
            'cliente': cliente,
            'origen': producto.get('origen', 'Desconocido'),
            'fecha': fecha
        }

        ventas = cls.todas()
        ventas.append(nueva_venta)
        if cls.storage.guardar(ventas):
            return nueva_venta, 201
        return {'error': 'No se pudo registrar la venta'}, 500

    @classmethod
    def obtener_estadisticas_ventas_por_dia(cls, fecha_inicio=None, fecha_fin=None):
        """
        Calcula las ventas totales (unidades vendidas) por día.
        Opcionalmente, puede filtrar por un rango de fechas.
        :param fecha_inicio: Fecha de inicio del rango (formato 'YYYY-MM-DD'). Opcional.
        :param fecha_fin: Fecha de fin del rango (formato 'YYYY-MM-DD'). Opcional.
        :return: Un diccionario con fechas como claves y total de unidades vendidas como valores.
        """
        ventas = cls.todas()
        estadisticas = {}
        for venta in ventas:
            try:
                venta_fecha_dt = datetime.strptime(venta['fecha'], '%Y-%m-%d').date()
                
                if fecha_inicio and fecha_fin:
                    inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
                    fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
                    if not (inicio_dt <= venta_fecha_dt <= fin_dt):
                        continue
                
                fecha = venta['fecha']
                estadisticas[fecha] = estadisticas.get(fecha, 0) + venta['cantidad']
            except (ValueError, KeyError):
                continue
        return estadisticas

    @classmethod
    def obtener_estadisticas_productos_mas_vendidos(cls, fecha_inicio=None, fecha_fin=None):
        """
        Calcula la cantidad total vendida de cada producto.
        Opcionalmente, puede filtrar por un rango de fechas.
        :param fecha_inicio: Fecha de inicio del rango (formato 'YYYY-MM-DD'). Opcional.
        :param fecha_fin: Fecha de fin del rango (formato 'YYYY-MM-DD'). Opcional.
        :return: Un diccionario ordenado por cantidad vendida (descendente).
        """
        ventas = cls.todas()
        estadisticas = {}
        for venta in ventas:
            try:
                venta_fecha_dt = datetime.strptime(venta['fecha'], '%Y-%m-%d').date()
                
                if fecha_inicio and fecha_fin:
                    inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
                    fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
                    if not (inicio_dt <= venta_fecha_dt <= fin_dt):
                        continue

                nombre_producto = venta['producto']
                estadisticas[nombre_producto] = estadisticas.get(nombre_producto, 0) + venta['cantidad']
            except (ValueError, KeyError):
                continue
        return dict(sorted(estadisticas.items(), key=lambda item: item[1], reverse=True))

    @classmethod
    def obtener_estadisticas_ventas_por_origen(cls, fecha_inicio=None, fecha_fin=None):
        """
        Calcula las ventas agrupadas por el origen del producto.
        Opcionalmente, puede filtrar por un rango de fechas.
        :param fecha_inicio: Fecha de inicio del rango (formato 'YYYY-MM-DD'). Opcional.
        :param fecha_fin: Fecha de fin del rango (formato 'YYYY-MM-DD'). Opcional.
        :return: Un diccionario con orígenes como claves y total de unidades vendidas como valores.
        """
        ventas = cls.todas()
        productos_map = {p['nombre']: p for p in Producto.todos()} # Usar un mapa para búsqueda rápida
        origenes_ventas = {}
        for venta in ventas:
            try:
                venta_fecha_dt = datetime.strptime(venta['fecha'], '%Y-%m-%d').date()
                
                if fecha_inicio and fecha_fin:
                    inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
                    fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
                    if not (inicio_dt <= venta_fecha_dt <= fin_dt):
                        continue

                nombre_producto = venta['producto']
                producto_obj = productos_map.get(nombre_producto) # Obtener del mapa
                
                if producto_obj and producto_obj.get('origen'):
                    origen = producto_obj['origen']
                    origenes_ventas[origen] = origenes_ventas.get(origen, 0) + venta['cantidad']
            except (ValueError, KeyError):
                continue
        return origenes_ventas


# --- RUTAS FLASK (ENDPOINTS DE LA API) ---

# --- Endpoints para PRODUCTOS ---
@app.route('/productos', methods=['GET'])
def get_productos():
    """
    Endpoint para obtener todos los productos.
    Responde a: GET /productos
    Retorna: Una lista JSON de todos los productos y un código de estado 200 (OK).
    """
    return jsonify(Producto.todos())

@app.route('/productos', methods=['POST'])
def post_producto():
    """
    Endpoint para crear un nuevo producto.
    Requiere un cuerpo JSON con 'nombre', 'stock' y 'origen'.
    Responde a: POST /productos
    Retorna: El producto creado y código 201 (Created), o un mensaje de error y un código apropiado.
    """
    resultado, codigo = Producto.crear(request.json)
    return jsonify(resultado), codigo

@app.route('/productos/<nombre>', methods=['GET'])
def get_producto(nombre):
    """
    Endpoint para obtener un producto específico por su nombre.
    Responde a: GET /productos/<nombre_del_producto>
    Retorna: El producto encontrado y código 200 (OK), o un error 404 (Not Found).
    """
    producto = Producto.buscar(nombre)
    if producto:
        return jsonify(producto)
    return jsonify({'error': f'Producto "{nombre}" no encontrado'}), 404

@app.route('/productos/<nombre>', methods=['PUT'])
def put_producto(nombre):
    """
    Endpoint para actualizar un producto existente por su nombre.
    Requiere un cuerpo JSON con los campos a actualizar.
    Responde a: PUT /productos/<nombre_del_producto>
    Retorna: El producto actualizado y código 200 (OK), o un error 404 (Not Found).
    """
    resultado, codigo = Producto.actualizar(nombre, request.json)
    return jsonify(resultado), codigo

@app.route('/productos/<nombre>', methods=['DELETE'])
def delete_producto(nombre):
    """
    Endpoint para eliminar un producto por su nombre.
    Responde a: DELETE /productos/<nombre_del_producto>
    Retorna: Un mensaje de éxito y código 200 (OK), o un error 404 (Not Found).
    """
    resultado, codigo = Producto.eliminar(nombre)
    return jsonify(resultado), codigo

# --- Endpoints para PERSONAS ---
@app.route('/personas', methods=['GET'])
def get_personas():
    """
    Endpoint para obtener todas las personas.
    Responde a: GET /personas
    Retorna: Una lista JSON de todas las personas y un código de estado 200 (OK).
    """
    return jsonify(Persona.todos())

@app.route('/personas', methods=['POST'])
def post_persona():
    """
    Endpoint para crear una nueva persona.
    Requiere un cuerpo JSON con al menos el 'nombre'.
    Responde a: POST /personas
    Retorna: La persona creada y código 201 (Created), o un mensaje de error y un código apropiado.
    """
    resultado, codigo = Persona.crear(request.json)
    return jsonify(resultado), codigo

@app.route('/personas/<nombre>', methods=['GET'])
def get_persona(nombre):
    """
    Endpoint para obtener una persona específica por su nombre.
    Responde a: GET /personas/<nombre_de_la_persona>
    Retorna: La persona encontrada y código 200 (OK), o un error 404 (Not Found).
    """
    persona = Persona.buscar(nombre)
    if persona:
        return jsonify(persona)
    return jsonify({'error': f'Persona "{nombre}" no encontrada'}), 404

@app.route('/personas/<nombre>', methods=['PUT'])
def put_persona(nombre):
    """
    Endpoint para actualizar una persona existente por su nombre.
    Requiere un cuerpo JSON con los campos a actualizar.
    Responde a: PUT /personas/<nombre_de_la_persona>
    Retorna: La persona actualizada y código 200 (OK), o un error 404 (Not Found).
    """
    resultado, codigo = Persona.actualizar(nombre, request.json)
    return jsonify(resultado), codigo

@app.route('/personas/<nombre>', methods=['DELETE'])
def delete_persona(nombre):
    """
    Endpoint para eliminar una persona por su nombre.
    Responde a: DELETE /personas/<nombre_de_la_persona>
    Retorna: Un mensaje de éxito y código 200 (OK), o un error 404 (Not Found).
    """
    resultado, codigo = Persona.eliminar(nombre)
    return jsonify(resultado), codigo

# --- Endpoints para VENTAS ---
@app.route('/ventas', methods=['GET'])
def get_ventas():
    """
    Endpoint para obtener todas las ventas registradas.
    Responde a: GET /ventas
    Retorna: Una lista JSON de todas las ventas y un código de estado 200 (OK).
    """
    return jsonify(Venta.todas())

@app.route('/ventas', methods=['POST'])
def post_venta():
    """
    Endpoint para registrar una nueva venta.
    Requiere un cuerpo JSON con 'producto' (un dict con 'nombre') y 'cantidad',
    opcionalmente 'cliente'.
    Responde a: POST /ventas
    Retorna: La venta registrada y código 201 (Created), o un mensaje de error y un código apropiado.
    """
    resultado, codigo = Venta.crear(request.json)
    return jsonify(resultado), codigo

@app.route('/ventas/cambiar_fecha', methods=['PUT'])
def cambiar_fecha_venta():
    """
    Endpoint para modificar la fecha de una venta específica.
    Requiere en el cuerpo JSON:
    - 'producto': Nombre del producto en la venta.
    - 'cliente': Nombre del cliente en la venta.
    - 'fecha_anterior': Fecha actual de la venta a modificar (YYYY-MM-DD).
    - 'nueva_fecha': La nueva fecha para la venta (YYYY-MM-DD).
    Responde a: PUT /ventas/cambiar_fecha
    Retorna: Un mensaje de éxito y código 200 (OK), o un mensaje de error y un código apropiado.
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Faltan datos en la petición"}), 400

    producto_nombre = data.get('producto')
    cliente = data.get('cliente')
    fecha_anterior = data.get('fecha_anterior')
    nueva_fecha = data.get('nueva_fecha')

    if not (producto_nombre and cliente and fecha_anterior and nueva_fecha):
        return jsonify({"error": "Faltan campos obligatorios: producto, cliente, fecha_anterior, nueva_fecha"}), 400

    ventas = Venta.todas()
    modificada = False

    for venta in ventas:
        if (
            venta.get('producto') == producto_nombre and
            venta.get('cliente') == cliente and
            venta.get('fecha') == fecha_anterior
        ):
            venta['fecha'] = nueva_fecha
            modificada = True
            break

    if not modificada:
        return jsonify({"error": "Venta no encontrada con los datos proporcionados"}), 404

    if Venta.storage.guardar(ventas):
        return jsonify({"mensaje": "Fecha de la venta actualizada correctamente"}), 200
    else:
        return jsonify({"error": "No se pudo guardar la modificación"}), 500

@app.route('/ventas/cancelar', methods=['DELETE'])
def cancelar_venta():
    """
    Endpoint para cancelar una venta específica y revertir el stock del producto.
    Requiere en el cuerpo JSON:
    - 'producto': Nombre del producto de la venta a cancelar.
    - 'cliente': Nombre del cliente de la venta a cancelar.
    - 'fecha': Fecha de la venta a cancelar (YYYY-MM-DD).
    Responde a: DELETE /ventas/cancelar
    Retorna: Un mensaje de éxito y código 200 (OK), o un mensaje de error y un código apropiado.
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Faltan datos en la petición"}), 400

    producto_nombre = data.get('producto')
    cliente = data.get('cliente')
    fecha = data.get('fecha')

    if not (producto_nombre and cliente and fecha):
        return jsonify({"error": "Debe enviar producto, cliente y fecha"}), 400

    ventas = Venta.todas()
    venta_encontrada = None
    indice_venta = -1
    for i, v in enumerate(ventas):
        if v.get('producto') == producto_nombre and v.get('cliente') == cliente and v.get('fecha') == fecha:
            venta_encontrada = v
            indice_venta = i
            break

    if venta_encontrada:
        cantidad_vendida = venta_encontrada.get('cantidad', 0)
        if cantidad_vendida <= 0:
            return jsonify({"error": "Cantidad de venta inválida para cancelar"}), 400

        ventas.pop(indice_venta)

        producto = Producto.buscar(producto_nombre)
        if producto:
            producto['stock'] += cantidad_vendida
            resultado_actualizacion, codigo_actualizacion = Producto.actualizar(producto['nombre'], producto)
            
            if codigo_actualizacion == 200:
                if Venta.storage.guardar(ventas):
                    return jsonify({"mensaje": "Venta cancelada y stock revertido correctamente"}), 200
                else:
                    return jsonify({"error": "Error al guardar los cambios en ventas después de revertir stock. Stock revertido."}), 500
            else:
                return jsonify({"error": f"Error al actualizar stock del producto '{producto_nombre}': {resultado_actualizacion.get('error')}"}), codigo_actualizacion
        else:
            return jsonify({"error": f"Error: Producto '{producto_nombre}' no encontrado para revertir el stock. Venta eliminada."}), 404
    else:
        return jsonify({"error": "Venta no encontrada"}), 404


# --- Endpoints para ESTADÍSTICAS ---
@app.route('/estadisticas/ventas_por_dia', methods=['GET'])
def get_estadisticas_ventas_por_dia():
    """
    Endpoint para obtener el total de unidades vendidas por día.
    Parámetros opcionales en la URL: 'fecha_inicio' y 'fecha_fin' (formato YYYY-MM-DD).
    Responde a: GET /estadisticas/ventas_por_dia?fecha_inicio=YYYY-MM-DD&fecha_fin=YYYY-MM-DD
    Retorna: Un diccionario JSON con fechas como claves y el total de unidades vendidas como valores.
    """
    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')
    estadisticas = Venta.obtener_estadisticas_ventas_por_dia(fecha_inicio, fecha_fin)
    return jsonify(estadisticas)

@app.route('/estadisticas/productos_mas_vendidos', methods=['GET'])
def get_estadisticas_productos_mas_vendidos():
    """
    Endpoint para obtener los productos más vendidos (por cantidad).
    Parámetros opcionales en la URL: 'fecha_inicio' y 'fecha_fin' (formato YYYY-MM-DD).
    Responde a: GET /estadisticas/productos_mas_vendidos?fecha_inicio=YYYY-MM-DD&fecha_fin=YYYY-MM-DD
    Retorna: Un diccionario JSON con nombres de productos como claves y la cantidad total vendida como valores,
             ordenado de forma descendente.
    """
    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')
    estadisticas = Venta.obtener_estadisticas_productos_mas_vendidos(fecha_inicio, fecha_fin)
    return jsonify(estadisticas)

@app.route('/estadisticas/ventas_por_origen', methods=['GET'])
def get_estadisticas_ventas_por_origen():
    """
    Endpoint para obtener las ventas agrupadas por el origen del producto.
    Parámetros opcionales en la URL: 'fecha_inicio' y 'fecha_fin' (formato YYYY-MM-DD).
    Responde a: GET /estadisticas/ventas_por_origen?fecha_inicio=YYYY-MM-DD&fecha_fin=YYYY-MM-DD
    Retorna: Un diccionario JSON con orígenes como claves y el total de unidades vendidas como valores.
    """
    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')
    estadisticas = Venta.obtener_estadisticas_ventas_por_origen(fecha_inicio, fecha_fin)
    return jsonify(estadisticas)


# --- Inicio de la aplicación ---
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)