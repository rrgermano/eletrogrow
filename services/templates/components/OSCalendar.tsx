
import React, { useState } from 'react';
import { ServiceOrder } from '../types';

interface OSCalendarProps {
  orders: ServiceOrder[];
  onSelectOrder: (os: ServiceOrder) => void;
}

const OSCalendar: React.FC<OSCalendarProps> = ({ orders, onSelectOrder }) => {
  const [currentDate, setCurrentDate] = useState(new Date());

  const daysInMonth = (year: number, month: number) => new Date(year, month + 1, 0).getDate();
  const firstDayOfMonth = (year: number, month: number) => new Date(year, month, 1).getDay();

  const year = currentDate.getFullYear();
  const month = currentDate.getMonth();

  const prevMonth = () => setCurrentDate(new Date(year, month - 1, 1));
  const nextMonth = () => setCurrentDate(new Date(year, month + 1, 1));

  const daysArr = [];
  const totalDays = daysInMonth(year, month);
  const startOffset = firstDayOfMonth(year, month);

  // Preencher dias vazios do início do mês
  for (let i = 0; i < startOffset; i++) daysArr.push(null);
  for (let d = 1; d <= totalDays; d++) daysArr.push(d);

  const getOrdersForDay = (day: number) => {
    const formattedDate = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
    return orders.filter(o => o.date === formattedDate);
  };

  const monthNames = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"];
  const weekDays = ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"];

  return (
    <div className="bg-white rounded-3xl shadow-xl border border-slate-200 overflow-hidden flex flex-col min-h-[800px]">
      {/* Calendar Header */}
      <div className="flex items-center justify-between p-8 bg-white border-b border-slate-100">
        <div className="flex flex-col">
          <span className="text-[10px] font-black text-emerald-600 uppercase tracking-[0.3em] mb-1">Visualização Mensal</span>
          <h2 className="text-3xl font-black text-slate-800 flex items-center gap-3">
            {monthNames[month]} <span className="text-slate-300 font-light">/ {year}</span>
          </h2>
        </div>
        <div className="flex gap-3 bg-slate-50 p-1.5 rounded-2xl border border-slate-200">
          <button onClick={prevMonth} className="w-10 h-10 flex items-center justify-center bg-white border border-slate-200 text-slate-600 hover:text-emerald-600 hover:border-emerald-200 rounded-xl transition-all">
            <i className="bi bi-chevron-left"></i>
          </button>
          <button onClick={() => setCurrentDate(new Date())} className="px-6 h-10 flex items-center justify-center bg-emerald-600 text-white font-bold rounded-xl shadow-md shadow-emerald-100 active:scale-95 transition-all text-sm">
            Hoje
          </button>
          <button onClick={nextMonth} className="w-10 h-10 flex items-center justify-center bg-white border border-slate-200 text-slate-600 hover:text-emerald-600 hover:border-emerald-200 rounded-xl transition-all">
            <i className="bi bi-chevron-right"></i>
          </button>
        </div>
      </div>

      {/* Week Day Titles */}
      <div className="grid grid-cols-7 bg-slate-50/50 border-b border-slate-100">
        {weekDays.map(day => (
          <div key={day} className="py-4 text-center font-black text-[10px] text-slate-400 uppercase tracking-widest">{day}</div>
        ))}
      </div>

      {/* Days Grid */}
      <div className="grid grid-cols-7 flex-grow divide-x divide-y divide-slate-100">
        {daysArr.map((day, idx) => {
          const dayOrders = day ? getOrdersForDay(day) : [];
          const isToday = day === new Date().getDate() && month === new Date().getMonth() && year === new Date().getFullYear();

          if (!day) return <div key={`empty-${idx}`} className="bg-slate-50/30"></div>;

          return (
            <div 
              key={`day-${day}`} 
              className={`min-h-[140px] p-3 transition-all relative group hover:bg-slate-50/50 ${isToday ? 'bg-emerald-50/20' : ''}`}
            >
              <div className="flex justify-between items-start mb-3">
                <span className={`text-sm font-black w-8 h-8 flex items-center justify-center rounded-xl transition-all ${
                  isToday 
                    ? 'bg-emerald-600 text-white shadow-lg shadow-emerald-100' 
                    : 'text-slate-400 group-hover:text-slate-800'
                }`}>
                  {day}
                </span>
                {dayOrders.length > 0 && (
                  <span className="text-[9px] bg-slate-800 text-white px-1.5 py-0.5 rounded-md font-bold uppercase tracking-tighter">
                    {dayOrders.length} OS
                  </span>
                )}
              </div>
              
              <div className="space-y-1.5 overflow-y-auto max-h-[120px] pr-1 custom-scrollbar">
                {dayOrders.map(os => (
                  <div
                    key={os.id}
                    onClick={() => onSelectOrder(os)}
                    className="text-[10px] p-2 rounded-lg border border-slate-200 bg-white hover:border-emerald-500 hover:shadow-md transition-all cursor-pointer truncate font-bold text-slate-700 flex items-center gap-2 group/item"
                  >
                    <span className={`w-2 h-2 rounded-full shrink-0 ${
                      os.status === 'Concluído' ? 'bg-emerald-500' :
                      os.status === 'Em Andamento' ? 'bg-amber-500' :
                      'bg-sky-500'
                    }`}></span>
                    <span className="truncate group-hover/item:text-emerald-700">#{os.id} {os.service}</span>
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default OSCalendar;
