document.addEventListener('DOMContentLoaded', function () {
  const calendarEl = document.getElementById('calendar');
  if (!calendarEl) return;
  const calendar = new FullCalendar.Calendar(calendarEl, {
    locale: 'pt-br',
    initialView: 'dayGridMonth',
    initialDate: '2026-09-16',
    height: 'auto',
    dayMaxEvents: 2,
    fixedWeekCount: false,
    headerToolbar: { left: 'prev,next today', center: 'title', right: 'dayGridMonth,listMonth' },
    buttonText: { today: 'Hoje', month: 'Mês', list: 'Lista' },
    events: '/api/events',
    eventClick: function (info) {
      const props = info.event.extendedProps;
      const detail = props.description ? `\n\n${props.description}` : '';
      alert(`${info.event.title}\nCategoria: ${props.category}${detail}`);
    }
  });
  calendar.render();
});
