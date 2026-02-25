# Blueprint del usuario, se hace para separar el codigo y dejar app.py limpio
from typing import Literal
from flask import Blueprint, request, session
from flask.wrappers import Response
from typing import Any
from src.dim_reservations.reservation_handler import ReservationService

from src.routes.handle_message import send_error, send_success

#Importaciones para crear cuenta
from src.utils.decorators import login_required

reservation_options = ReservationService()
reservation_route = Blueprint('reservation_route', __name__, url_prefix='/api/reservation/')

from flask_jwt_extended import jwt_required,  get_jwt, get_jwt_identity

@reservation_route.route('/create', methods=['POST'])
@login_required
def create_reservation() -> tuple[Any]:
    """
    Crea una nueva reserva en la tabla dim_people
    """
    try: 
        data_reservation = request.get_json()

        # --- INYECCIÓN DEL ID DE SESIÓN ---
        # Tomamos el ID del usuario logueado y lo agregamos a los datos
        data_reservation['DIM_ServiceOwnersId'] = session['user_id']

        for name in data_reservation:
            print(f"'{name}': {data_reservation[name]}", end="\n")
        status, message = reservation_options.create_reservation(data_reservation)
        
        if status != 201:
            print(message)
            return send_error(message, status)
        
        return send_success("Reserva creada exitosamente", None, 201)
    except Exception as e:
        print(e)
        return send_error(str(e), 500)



@reservation_route.route('/read', methods=['GET'])
@login_required
def read_reservation():
    """
    Obtiene reservas por fecha desde los parámetros de consulta
    """
    try:
        # Obtener la fecha del parámetro de consulta 'date'
        date = request.args.get('date')
        
        # Validar que la fecha fue proporcionada
        if not date:
            return send_error("El parámetro 'date' es requerido", 400)
        
        status, data_reservations = reservation_options.read_reservations_by_date(date)
        
        if status != 200:
            return send_error("Error al obtener las reservas", status)
        
        return send_success("Reservas obtenidas exitosamente", data_reservations, 200)
    
    except Exception as e:
        print(e)
        return send_error(str(e), 500)
    

@reservation_route.route('/update', methods=['POST'])
@login_required
def update_reservation():
    """
    Actualiza una reserva existente
    """
    try:
        # Usar directamente el reservation_id de la URL
        data_reservation = request.get_json()
        status, message, new_data = reservation_options.update_reservation(data_reservation)
        
        if status != 200:
            return send_error(message, status)
        
        return send_success("Reserva actualizada exitosamente", new_data, 200)
    except Exception as e:
        return send_error(str(e), 500)
    
@reservation_route.route('/get_contract', methods=['POST'])
@login_required
def get_contract():
    """
    Obtiene la informacion de una reservacion, para mostrarla como contrato
    """
    try:
        #print("Se creo el endpoint  y conecto")
        #return send_success("Reserva obtenida exitosamente", None, 200)
        # Obtener la fecha del parámetro de consulta 'date'
        reservation_id = request.get_json()
        
        # Validar que la fecha fue proporcionada
        if not reservation_id:
            return send_error("El parámetro 'reservation_id' es requerido", 400)
        
        status, message, data_reservations = reservation_options.get_contracto_info(reservation_id) # metodo aun no creado
        
        if status != 200:
            return send_error(message, status)
        
        return send_success(message, data_reservations, status)
    
    except Exception as e:
        print(e)
        return send_error(str(e), 500)


@reservation_route.route('/archive', methods=['POST'])
@login_required
def archive_reservation() -> tuple[Any]:
    """
    Archiva lógicamente una reserva existente utilizando el ID proporcionado en el cuerpo de la solicitud (JSON).

    Esta operación realiza un 'soft delete' de la reserva.
    """
    try: 
        # Se espera que el JSON contenga el ID de la reserva a archivar
        id_reservation = request.get_json()
        print(id_reservation)
        
        # Llama a la función de lógica de negocio para archivar la reserva
        # Se asume que delete_reservation realiza el archivado lógico
        # TODO: Cambiar el nombre de la función en reservation_options a algo más claro como 'archive_reservation_by_id'

        status, message, data  = reservation_options.archivate_reservation(id_reservation)

        # Si el estado de la operación no es de éxito (asumimos 200 OK para el éxito del archivo lógico)
        if status != 200:
            print(message)
            # Devuelve el error con el status code devuelto por la lógica de negocio
            return send_error(message, status)
        
        # Operación exitosa
        # Un archivo o eliminación exitosa suele retornar 200 OK
        return send_success("Reserva archivada exitosamente", data, 200)
    
    except Exception as e:
        # Manejo de errores internos del servidor (ej. error de conexión, JSON inválido, etc.)
        print(f"Error interno al archivar la reserva: {e}")
        return send_error(str(e), 500)


@reservation_route.route('/cancel', methods=['POST'])
@login_required
def cancel_reservation() -> tuple[Any]:
    """
    Cancela una reserva existente
    """
    try:
        id_reservation = request.get_json()
        status, message, data = reservation_options.cancelled_reservation(id_reservation)
        
        if status != 200:
            print(message)
            return send_error(message, status)
        
        return send_success(message, data, 200)
    except Exception as e:
        print(e)
        return send_error(str(e), 500)

@reservation_route.route('/prueba1', methods=['GET'])
@login_required
def prueba1() -> tuple[Any]:
    """
    Crea una nueva reserva en la tabla dim_people
    """
    try:
        return send_success("Prueba creada exitosamente", None, 200)
    except Exception as e:
        print(e)
        return send_error(str(e), 500)
    

@reservation_route.route('/stats_calendar', methods=['GET'])
@login_required
def stats_calendar() -> tuple[Any]:
    """
    Obtiene estadísticas de reservas para el calendario según los parámetros de consulta

    """
    try:
        # Obtener los parámetros de consulta
        filter_type = request.args.get('filter_type')  # 'day', 'week', 'month', 'year'
        year = request.args.get('year', type=int)  # Año es obligatorio
        month = request.args.get('month', type=int)  # Mes es opcional, solo necesario para 'month'
        # Validar que el tipo de filtro es válido
        if filter_type not in ['day', 'week', 'month', 'year']:
            return send_error("El parámetro 'filter_type' debe ser uno de: 'day', 'week', 'month', 'year'", 400)
        if not year:
            return send_error("El parámetro 'year' es obligatorio", 400)
        if filter_type == 'month' and not month:
            return send_error("El parámetro 'month' es obligatorio para el filtro tipo 'month'", 400)
        
        # Construir el diccionario que espera el handler
        request_data = {
            'filter_type': filter_type,
            'year': year,
            'month': month
        }
        # Llamar a la función de lógica de negocio para obtener las estadísticas
        status, message, data_stats = reservation_options.get_reservation_stats(request_data)
        if status != 200:
            print(message)
            return send_error(message, status)
        return send_success(message, data_stats, 200)
    except Exception as e:
        print(e)
        return send_error(str(e), 500)