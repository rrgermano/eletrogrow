
import React, { useState, useMemo, useEffect } from 'react';
import { ServiceOrder, ViewType, DashboardStats } from './types';
import { MOCK_ORDERS } from './constants';
import OSList from './components/OSList';
import OSCalendar from './components/OSCalendar';
import OSDetailSidebar from './components/OSDetailSidebar';
import AIAssistant from './components/AIAssistant';

const App: React.FC = () => {
  const [view, setView] = useState<ViewType>('calendar'); 
  const [searchTerm, setSearchTerm] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [selectedOrder, setSelectedOrder] = useState<ServiceOrder | null>(null);
  const [isMobile, setIsMobile] = useState(window.innerWidth < 768);

  useEffect(() => {
    const handleResize = () => setIsMobile(window.innerWidth < 768);
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const filteredAndSortedOrders = useMemo(() => {
    return MOCK_ORDERS
      .filter(order => {
        const matchesSearch = order.service.toLowerCase().includes(searchTerm.toLowerCase()) ||
                              order.customer.toLowerCase().includes(searchTerm.toLowerCase()) ||
                              (order.project && order.project.toLowerCase().includes(searchTerm.toLowerCase()));
        const matchesDateRange = (!startDate || order.date >= startDate) &&
                                 (!endDate || order.date <= endDate);
        return matchesSearch && matchesDateRange;
      })
      .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());
  }, [searchTerm, startDate, endDate]);

  const stats = useMemo<DashboardStats>(() => {
    return {
      totalValue: filteredAndSortedOrders.reduce((acc, o) => acc + o.value, 0),
      pendingCount: filteredAndSortedOrders.filter(o => o.status === 'Pendente').length,
      completedCount: filteredAndSortedOrders.filter(o => o.status === 'Concluído').length,
      ongoingCount: filteredAndSortedOrders.filter(o => o.status === 'Em Andamento').length,
    };
  }, [filteredAndSortedOrders]);

  return (
    <div className="min-h-screen bg-[#f8fafc] text-slate-900 font-sans">
      {/* Sidebar Detail Overlay */}
      {selectedOrder && (
        <div 
          className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm z-40 transition-opacity" 
          onClick={() => setSelectedOrder(null)} 
        />
      )}
      <OSDetailSidebar order={selectedOrder} onClose={() => setSelectedOrder(null)} />

      <div className="max-w-[1600px] mx-auto px-4 md:px-8 py-8">
        {/* Header */}
        <header className="mb-8 flex flex-col lg:flex-row lg:items-center justify-between gap-6">
          <div>
            <div className="flex items-center gap-3 text-emerald-600 font-bold text-xs uppercase tracking-[0.2em] mb-2">
              <span className="w-10 h-[2px] bg-emerald-600"></span>
              Sistema de Gestão ERP
            </div>
            <h1 className="text-4xl font-black text-slate-800 tracking-tight">Ordens de Serviço</h1>
          </div>
          
          <div className="flex bg-white p-1 rounded-2xl shadow-sm border border-slate-200">
            <button
              onClick={() => setView('list')}
              className={`flex items-center gap-2 px-6 py-2.5 rounded-xl text-sm font-bold transition-all ${view === 'list' ? 'bg-emerald-600 text-white shadow-lg' : 'text-slate-400 hover:text-slate-600'}`}
            >
              <i className="bi bi-list-ul text-lg"></i> Lista
            </button>
            <button
              onClick={() => setView('calendar')}
              className={`flex items-center gap-2 px-6 py-2.5 rounded-xl text-sm font-bold transition-all ${view === 'calendar' ? 'bg-emerald-600 text-white shadow-lg' : 'text-slate-400 hover:text-slate-600'}`}
            >
              <i className="bi bi-calendar3 text-lg"></i> Calendário
            </button>
          </div>
        </header>

        {/* Filters Bar */}
        <div className="bg-white p-5 rounded-2xl shadow-sm border border-slate-200 mb-8 flex flex-col lg:flex-row gap-5 items-stretch">
          <div className="relative flex-grow">
            <i className="bi bi-search absolute left-4 top-1/2 -translate-y-1/2 text-slate-400"></i>
            <input
              type="text"
              placeholder="Buscar por serviço, cliente ou projeto..."
              className="w-full pl-12 pr-4 py-3 bg-slate-50 border-2 border-slate-100 rounded-xl focus:outline-none focus:border-emerald-500 focus:bg-white transition-all text-sm"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          
          <div className="flex flex-wrap gap-3 items-center">
            <div className="flex items-center gap-2 px-3 py-2 bg-slate-50 border-2 border-slate-100 rounded-xl">
              <span className="text-[10px] font-bold text-slate-400 uppercase">Início</span>
              <input 
                type="date" 
                className="bg-transparent text-sm font-medium outline-none" 
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
              />
            </div>
            <div className="flex items-center gap-2 px-3 py-2 bg-slate-50 border-2 border-slate-100 rounded-xl">
              <span className="text-[10px] font-bold text-slate-400 uppercase">Fim</span>
              <input 
                type="date" 
                className="bg-transparent text-sm font-medium outline-none" 
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
              />
            </div>
            <button className="bg-emerald-600 hover:bg-emerald-700 text-white px-6 py-3 rounded-xl font-bold shadow-md shadow-emerald-200 transition-all active:scale-95 flex items-center gap-2 whitespace-nowrap">
              <i className="bi bi-plus-lg"></i> Nova OS
            </button>
          </div>
        </div>

        {/* Stats Summary for List View */}
        {view === 'list' && (
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
            <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm group hover:border-emerald-200 transition-all">
              <p className="text-slate-400 text-[10px] font-black uppercase tracking-wider mb-1">Total em Aberto</p>
              <h3 className="text-2xl font-black text-emerald-600">R$ {stats.totalValue.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}</h3>
            </div>
            <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
              <p className="text-slate-400 text-[10px] font-black uppercase tracking-wider mb-1">Pendentes</p>
              <h3 className="text-2xl font-black text-slate-800">{stats.pendingCount}</h3>
            </div>
            <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
              <p className="text-slate-400 text-[10px] font-black uppercase tracking-wider mb-1">Em Execução</p>
              <h3 className="text-2xl font-black text-amber-500">{stats.ongoingCount}</h3>
            </div>
            <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
              <p className="text-slate-400 text-[10px] font-black uppercase tracking-wider mb-1">Concluídas</p>
              <h3 className="text-2xl font-black text-sky-600">{stats.completedCount}</h3>
            </div>
          </div>
        )}

        {/* Main Content Area */}
        <main className="pb-16">
          {view === 'list' ? (
            <OSList orders={filteredAndSortedOrders} isMobile={isMobile} onSelectOrder={setSelectedOrder} />
          ) : (
            <div className="animate-in fade-in duration-500 slide-in-from-bottom-2">
              <OSCalendar orders={filteredAndSortedOrders} onSelectOrder={setSelectedOrder} />
            </div>
          )}

          {filteredAndSortedOrders.length === 0 && (
            <div className="text-center py-24 bg-white rounded-2xl border-2 border-dashed border-slate-200 mt-4 flex flex-col items-center">
               <div className="w-16 h-16 bg-slate-50 rounded-full flex items-center justify-center mb-4">
                 <i className="bi bi-search text-3xl text-slate-200"></i>
               </div>
               <h3 className="text-lg font-bold text-slate-400">Nenhuma ordem de serviço encontrada</h3>
               <p className="text-sm text-slate-300">Tente ajustar seus termos de busca ou filtros de data.</p>
            </div>
          )}
        </main>

        <AIAssistant orders={filteredAndSortedOrders} />
      </div>
    </div>
  );
};

export default App;
