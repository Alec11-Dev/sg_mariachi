/**
 * Agenda del sistema para el Mariachi San Nicolás
 * Preparada para navegación completa y eventos reales con panel lateral de detalles
 */
import { GetReservationStatsCalendar } from "../../api/api_reservation_stats_calendar.js";

document.addEventListener('DOMContentLoaded', function () {

  const calendarEl = document.getElementById('calendar');
  const detailPanel = document.getElementById('detailPanel');
  const panelContent = document.getElementById('panelContent');
  const closePanelBtn = document.getElementById('closePanel');

  // Inicialización del calendario
  const calendar = new FullCalendar.Calendar(calendarEl, {
    locale: 'es',
    initialView: 'timeGridWeek',
    allDaySlot: true, 
    height: 'auto',
    headerToolbar: false,

    // Función para agregar los eventos desde la API (Solución al bug de Año)
    events: async function(fetchInfo, successCallback, failureCallback) {
      try {
        const start = fetchInfo.start;
        const end = fetchInfo.end;
        const diffDays = (end - start) / (1000 * 60 * 60 * 24);
        
        // Si pide más de 100 días, estamos en la vista de Año
        const isYearView = diffDays > 100; 

        const midDate = new Date((start.getTime() + end.getTime()) / 2);
        const year = midDate.getFullYear();
        
        let rawData = [];

        if (isYearView) {
          // VISTA DE AÑO: Pedimos los 12 meses en paralelo para saber los días exactos
          const promesas = [];
          for (let m = 1; m <= 12; m++) {
            // Hacemos la petición de cada mes. Si un mes falla o no tiene datos, devolvemos un array vacío
            promesas.push(GetReservationStatsCalendar('month', year, m).catch(() => []));
          }
          
          const resultadosMeses = await Promise.all(promesas);
          
          // Combinamos los datos y les inyectamos a qué mes pertenecen
          resultadosMeses.forEach((mesData, index) => {
            const mesActual = index + 1;
            if (mesData && mesData.length > 0) {
              mesData.forEach(item => {
                rawData.push({ ...item, monthForDate: mesActual });
              });
            }
          });

        } else {
          // VISTA NORMAL (Mes/Semana/Día): Pedimos solo el mes actual
          const month = midDate.getMonth() + 1; 
          const data = await GetReservationStatsCalendar('month', year, month);
          if (data && data.length > 0) {
            data.forEach(item => {
              rawData.push({ ...item, monthForDate: month });
            });
          }
        }

        // MAPEAMOS LOS DATOS PARA EL CALENDARIO (Ahora siempre son fechas exactas)
        const formattedEvents = rawData.map(item => {
          const mesFormateado = String(item.monthForDate).padStart(2, '0');
          const diaFormateado = String(item.label).padStart(2, '0');
          const dateString = `${year}-${mesFormateado}-${diaFormateado}`;

          return {
            id: `stat-${dateString}`, // ID único basado en la fecha
            title: `${item.total_events} reserva(s)`, 
            start: dateString,
            allDay: true, 
            backgroundColor: '#0d6efd',
            extendedProps: {
              total: item.total_events
            }
          };
        });

        successCallback(formattedEvents);
      } catch (error) {
        console.error("Error al cargar las reservas:", error);
        failureCallback(error);
      }
    },

    // --- ACCIÓN AL HACER CLIC EN EL EVENTO ---
    eventClick: function(info) {
      const fecha = info.event.start;
      const totalReservas = info.event.extendedProps.total;

      // 1. Cambiamos la vista del calendario a 'Día' en la fecha seleccionada
      calendar.changeView('timeGridDay', fecha);

      // 2. Actualizamos los botones de vista para que el botón de 'Día' se vea activo
      document.querySelectorAll('.view-btn').forEach(btn => btn.classList.remove('active'));
      document.getElementById('day').classList.add('active');

      // 3. Llamamos a la función para abrir el panel profesional con los detalles
      openDetailPanel(fecha, totalReservas);
    },

    // Código para la vista de año
    views: {
      multiMonthYear: {
        type: 'multiMonth',
        duration: { years: 1 },
        buttonText: 'Año'
      }
    },

    // Actualiza el título del dashboard al cambiar fecha o vista
    datesSet: function () {
      updateCurrentDate(calendar);
    }
  });

  calendar.render();
  updateCurrentDate(calendar);

  /* --- FUNCIONES PARA MANEJAR EL PANEL DE DETALLES --- */
  function openDetailPanel(date, total) {
    const opcionesFecha = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
    const fechaFormateada = date.toLocaleDateString('es-ES', opcionesFecha).toUpperCase();

    const htmlContent = `
      <div class="date-summary">
        <span class="material-icons date-icon">event_note</span>
        <div>
          <h3>${fechaFormateada}</h3>
          <p>Resumen diario de reservas agendadas.</p>
        </div>
      </div>
      <div class="stats-box">
        <span class="material-icons total-icon">people_alt</span>
        <div class="total-count">
          <h4>TOTAL</h4>
          <span class="reservations-total">${total} reserva(s)</span>
        </div>
      </div>
    `;

    panelContent.innerHTML = htmlContent;
    detailPanel.classList.add('open');
  }

  closePanelBtn.onclick = function() {
    detailPanel.classList.remove('open');
  }

  /* BOTONES DE NAVEGACIÓN */
  document.getElementById('prev').onclick = () => calendar.prev();
  document.getElementById('next').onclick = () => calendar.next();
  document.getElementById('today').onclick = () => calendar.today();

  /* CAMBIO DE VISTAS */
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