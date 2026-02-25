/**
 * Agenda del sistema
 * Preparada para navegación completa y eventos reales
 */
import { GetReservationStatsCalendar } from "../../api/api_reservation_stats_calendar.js";

document.addEventListener('DOMContentLoaded', function () {

  const calendarEl = document.getElementById('calendar');

  // Inicialización del calendario
  const calendar = new FullCalendar.Calendar(calendarEl, {
    locale: 'es',
    initialView: 'timeGridWeek',
    allDaySlot: false,
    height: 'auto',
    headerToolbar: false,

    // Función para obtener eventos desde la API (con manejo de error visual)
    events: async function (fetchInfo, successCallback, failureCallback) {
      try {
        const start = fetchInfo.start;
        const end = fetchInfo.end;
        const diffDays = (end - start) / (1000 * 60 * 60 * 24);
        const filterType = diffDays > 100 ? 'year' : 'month';
        const midDate = new Date((start.getTime() + end.getTime()) / 2);
        const year = midDate.getFullYear();
        const month = midDate.getMonth() + 1;

        const rawData = await GetReservationStatsCalendar(
          filterType,
          year,
          filterType === 'month' ? month : null
        );

        const formattedEvents = rawData.map(item => ({
          id: item.id,
          title: item.nombre_reserva || 'Reserva',
          start: item.fecha_inicio,
          end: item.fecha_fin,
          backgroundColor: '#0d6efd'
        }));

        successCallback(formattedEvents);
      } catch (error) {
        console.error("Error al cargar las reservas:", error);
        // Muestra un evento de fondo rojo hoy para indicar el error
        successCallback([{
          title: 'Error al cargar eventos',
          start: new Date().toISOString().split('T')[0],
          allDay: true,
          backgroundColor: '#dc3545',
          textColor: 'white',
          display: 'background' // Aparece como fondo del día
        }]);
      }
    }, // <-- ¡IMPORTANTE! Esta coma separa 'events' de 'views'

    // Código para la vista de año
    views: {
      multiMonthYear: {
        type: 'multiMonth',
        duration: { years: 1 },
        buttonText: 'Año'
      }
    },

    // Actualiza el título al cambiar fecha o vista
    datesSet: function () {
      updateCurrentDate(calendar);
    }
  });

  calendar.render();
  updateCurrentDate(calendar);

  // Navegación
  document.getElementById('prev').onclick = () => calendar.prev();
  document.getElementById('next').onclick = () => calendar.next();
  document.getElementById('today').onclick = () => calendar.today();

  // Cambio de vistas
  function changeView(view, button) {
    calendar.changeView(view);
    document.querySelectorAll('.view-btn').forEach(btn => btn.classList.remove('active'));
    button.classList.add('active');
  }

  document.getElementById('day').onclick = function () {
    changeView('timeGridDay', this);
  };
  document.getElementById('week').onclick = function () {
    changeView('timeGridWeek', this);
  };
  document.getElementById('month').onclick = function () {
    changeView('dayGridMonth', this);
  };
  document.getElementById('year').onclick = function () {
    changeView('multiMonthYear', this);
  };

});

/**
 * Actualiza el título según la vista actual (mes y año)
 */
function updateCurrentDate(calendar) {
  const date = calendar.getDate();
  const viewType = calendar.view.type;
  let text = '';

  if (viewType === 'multiMonthYear' || viewType === 'dayGridYear') {
    text = date.getFullYear();
  } else {
    const options = { month: 'long', year: 'numeric' };
    text = date.toLocaleDateString('es-ES', options);
    text = text.charAt(0).toUpperCase() + text.slice(1);
  }

  document.getElementById('currentDate').textContent = text;
}