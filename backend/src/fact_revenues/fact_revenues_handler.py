from src.dim_dates.dim_date import DIM_DATE
from src.fact_revenues.fact_revenues_service import FactRevenuesService
from src.fact_revenues.fact_revenues_model import FactRevenues
from src.dim_reservations.repositorio.get_reservation_by_id import get_reservation_by_id
from src.fact_revenues.repositorio.get_total_paid import get_total_paid
from src.utils.conexion import Conexion
from src.utils.id_generator import create_id_fact_reservation
from datetime import datetime

class FactRevenuesHandler:
    def __init__(self):
        pass

    def create_revenue(self, _revenue: dict, conn: Conexion = None) -> tuple:
        """
        Crea un nuevo registro de ingresos facturados.

        Args:
            revenue_data (dict): Diccionario con los datos del ingreso facturado.

        Returns:
            FactRevenues: Objeto FactRevenues creado.
        """
        conexion = conn or Conexion()
        fact_revenue_service = FactRevenuesService(conexion)
        
        try:

            # 1. Validar que todos los campos necesarios estén presentes
            # FACT_RevenueId se genera aquí, no debe venir del request
            required_fields = ['FACT_PaymentAmount', 'DIM_DateId', 'DIM_ReservationId']
            for field in required_fields:
                if field not in _revenue:
                    return 400, f"Falta el campo requerido: {field}", []

            #2. Crear el objeto FactRevenues
            revenue = FactRevenues(
                FACT_RevenueId="", # Se genera abajo
                #FACT_PaymentAmount=_revenue['FACT_PaymentAmount'],
                FACT_PaymentAmount=float(_revenue['FACT_PaymentAmount']), # Asegurar conversión a float
                DIM_DateId=_revenue['DIM_DateId'],
                DIM_ReservationId=_revenue['DIM_ReservationId']
             )

            # 3. Validar que la factura no sea negativa
            # Se permite cualquier monto positivo para facilitar abonos y liquidaciones pequeñas
            if revenue.FACT_PaymentAmount <= 0:
                return 400, "El monto del pago debe ser mayor a 0.", []
            
            # Validar que el pago no exceda el monto restante de la reserva
            reservation = get_reservation_by_id(_revenue['DIM_ReservationId'], conexion)
            if not reservation:
                return 404, f"No se encontró la reserva {_revenue['DIM_ReservationId']}", []

            total_amount = float(reservation['DIM_TotalAmount'])
            total_paid = get_total_paid(_revenue['DIM_ReservationId'], conexion)
            remaining_balance = total_amount - total_paid

            # Si el pgo del evento se completo, no se permiten más pagos y se mostrara un mensaje indicando que la reserva ya está completamente pagada
            if total_paid == total_amount:
                return 400, "La reserva ya está completamente pagada. No se permiten más pagos.", []

            if revenue.FACT_PaymentAmount > remaining_balance:
                return 400, f"El monto del pago excede el saldo pendiente. Restante: {remaining_balance}", []
            
            #4. Generar el ID de la factura ya que no se proporciona
            # Agregamos datetime.now() para evitar IDs duplicados si se hacen 2 pagos el mismo día
            fact_id = create_id_fact_reservation([_revenue['DIM_DateId'], _revenue['DIM_ReservationId'], str(datetime.now())])
            revenue.FACT_RevenueId = fact_id
            print(revenue.FACT_RevenueId)

            # Para asegurar que el dim_date_id registre la fecha actual,
            # podríamos validar que el DIM_DateId proporcionado corresponde a la fecha actual.
            dim_date_service = DIM_DATE(conexion)
            current_date_id = dim_date_service.dateId
            if revenue.DIM_DateId != current_date_id:
                return 400, f"El DIM_DateId proporcionado no corresponde a la fecha actual. Se esperaba {current_date_id}", []

            # 3. Usar el servicio para crear el ingreso facturado
            created = fact_revenue_service.create_revenue(revenue)
            if not created:
                return 500, "Error al crear el ingreso facturado", []

            return 201, "Ingreso facturado creado correctamente", revenue
        except Exception as e:
            return 500, f"Error interno del servidor: {e}", []
        finally:
            if not conn:
                conexion.close_conexion()


    def get_revenue_info(self, _revenue: dict, conn: Conexion = None) -> tuple:
        """
        Obtiene la información de la reserva que se le aplicará el pago.
        Args:
            revenue_id (str): ID del ingreso facturado.

        Returns:
            dict: Diccionario con la información del ingreso facturado.
        """
        
        conexion = conn or Conexion()
        fact_revenue_service = FactRevenuesService(conexion)
        try:

            #1. Validar que el campo necesario esté presente
            required_fields = ['FACT_PaymentAmount', 'DIM_DateId', 'DIM_ReservationId']

            for field in required_fields:
                if field not in _revenue:
                    return 400, f"Falta el campo requerido: {field}", []
                
            # Reserva a la que se le aplicara el pago
            reservation_id = _revenue['DIM_ReservationId']

            #2. Obtener la información del ingreso facturado
            existing_revenue = fact_revenue_service.get_fact_revenues_by_id(
                reservation_id
            ) 

            return 200, "Información obtenida correctamente", existing_revenue
        except Exception as e:
            return 500, f"Error interno del servidor: {e}", []
        

    def get_revenue_statistics(self, request_data: dict, conn: Conexion = None) -> tuple:
        """
        Obtiene las estadísticas de ganancias para las gráficas.
        
        Args:
            request_data (dict): Puede contener 'filter_type' (month, week, year) y 'year'.
        
        Returns:
            tuple: (status, message, data)
        """
        conexion = conn or Conexion()
        fact_revenue_service = FactRevenuesService(conexion)
        
        try:
            # Valores por defecto: filtro por mes y año actual
            filter_type = request_data.get('filter_type', 'month')
            year_from_request = request_data.get('year')
            
            # Si el año no viene en el request o es nulo, usar el actual.
            # Si viene, convertirlo a entero.
            year = int(year_from_request) if year_from_request else datetime.now().year
            stats = fact_revenue_service.get_revenue_statistics(filter_type, year)
            
            return 200, "Estadísticas obtenidas correctamente", stats
            
        except Exception as e:
            return 500, f"Error interno del servidor: {e}", []
        finally:
            if not conn:
                conexion.close_conexion()