import axiosInstance from "./axiosInstance";

export const GetReservationStatsCalendar = async (filterType, year, month = null) => {
    try {
        console.log("Filtros enviados a api/reservation/stats_calendar:", { filterType, year, month });

        const params = { 
            filter_type: filterType,
            year: year 
        };

        if (month) {
            params.month = month;
        }

        // Hacer la petición GET con los parámetros correctos que espera el backend
        const response = await axiosInstance.get('reservation/stats_calendar', {
            params: params
        });
        console.log("Respuesta del servidor al obtener estadísticas de reservas para el calendario:", response.data);
        return response.data.body;

    } catch (error) {
        // Manejo mejorado de errores
        let errorMessage = 'Error desconocido al obtener las estadísticas de reservas para el calendario';

        if (error.response) {
            // El servidor respondió con un status fuera del rango 2xx
            errorMessage = `Error del servidor: ${error.response.status} - ${error.response.data?.message || 'Error desconocido'}`;
        } else if (error.request) {
            // No se recibió respuesta del servidor
            errorMessage = 'No se recibió respuesta del servidor';
        }
        console.error("Error al obtener estadísticas de reservas para el calendario:", errorMessage);
        throw new Error(errorMessage);

    }
}