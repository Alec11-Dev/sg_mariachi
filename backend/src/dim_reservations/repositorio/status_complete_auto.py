from src.utils.conexion import Conexion
from datetime import datetime
import pytz

def update_past_reservations_to_complete(connection: Conexion) -> int:
    """
    Busca reservaciones con estatus 'Pendiente' cuya fecha de fin (DIM_EndDate)
    ya haya pasado y actualiza su estatus a 'Completada'.
    
    Retorna el número de filas actualizadas.
    """
    # IDs obtenidos de tu contexto (reservation_handler.py)
    PENDING_STATUS_ID = '6d0fa47f-1933-5928'   # ID de Pendiente
    COMPLETED_STATUS_ID = 'd9664265-818c-52dc' # ID de Completada

    # Obtenemos la hora actual en formato ISO compatible con la BD
    # Usamos la zona horaria de México para asegurar consistencia
    mexico_tz = pytz.timezone("America/Mexico_City")
    current_time = datetime.now(mexico_tz).strftime('%Y-%m-%dT%H:%M:%S')

    query = """
    UPDATE dim_reservation
    SET DIM_StatusId = %s
    WHERE DIM_StatusId = %s
    AND DIM_EndDate < %s
    """

    try:
        connection.cursor.execute(query, (COMPLETED_STATUS_ID, PENDING_STATUS_ID, current_time))
        rows_affected = connection.cursor.rowcount
        
        if rows_affected > 0:
            connection.save_changes()
            print(f"🔄 Auto-Completado: Se actualizaron {rows_affected} reservaciones vencidas.")
            
        return rows_affected
    except Exception as e:
        print(f"❌ Error al ejecutar auto-completado de reservaciones: {e}")
        return 0
