
import React from 'react';
import { ServiceOrder } from '../types';

interface OSDetailSidebarProps {
  order: ServiceOrder | null;
  onClose: () => void;
}

const OSDetailSidebar: React.FC<OSDetailSidebarProps> = ({ order, onClose }) => {
  if (!order) return null;

  const statusColors = {
    'Pendente': 'bg-blue-100 text-blue-700 border-blue-200',
    'Em Andamento': 'bg-amber-100 text-amber-700 border-amber-200',
    'Concluído': 'bg-emerald-100 text-emerald-700 border-emerald-200',
    'Cancelado': 'bg-rose-100 text-rose-700 border-rose-200'
  };

  return (
    <div className="fixed inset-y-0 right-0 w-full md:w-[450px] bg-white shadow-[-10px_0_30px_rgba(0,0,0,0.1)] z-50 transform transition-transform duration-300 ease-in-out flex flex-col border-l-2 border-[#ddd]">
      <div className="p-6 border-b-2 border-[#ddd] flex justify-between items-center bg-[#f2f2f2]">
        <h3 className="text-xl font-black text-gray-800 uppercase tracking-tight">Editar Ordem # {order.id}</h3>
        <button onClick={onClose} className="p-2 hover:bg-gray-200 rounded-lg text-gray-500 transition-colors">
          <i className="bi bi-x-lg text-xl"></i>
        </button>
      </div>
      
      <div className="flex-grow p-8 overflow-y-auto space-y-6">
        <div className="grid grid-cols-2 gap-6">
           <div>
            <label className="text-[10px] font-black text-gray-400 uppercase mb-1 block">Status Atual</label>
            <div className={`inline-block px-3 py-1 rounded-md text-xs font-bold border-2 ${statusColors[order.status]}`}>
              {order.status}
            </div>
          </div>
          <div>
            <label className="text-[10px] font-black text-gray-400 uppercase mb-1 block">Data da OS</label>
            <input type="date" value={order.date} readOnly className="w-full bg-[#f5f5f5] border-2 border-[#ddd] rounded-md p-2 text-sm" />
          </div>
        </div>

        <div>
          <label className="text-[10px] font-black text-gray-400 uppercase mb-1 block">Serviço / Título</label>
          <input 
            type="text" 
            defaultValue={order.service} 
            className="w-full border-2 border-[#ddd] rounded-md p-3 text-lg font-bold focus:border-[#0096c7] focus:outline-none transition-all"
          />
        </div>

        <div>
          <label className="text-[10px] font-black text-gray-400 uppercase mb-1 block">Cliente</label>
          <input 
            type="text" 
            defaultValue={order.customer} 
            className="w-full border-2 border-[#ddd] rounded-md p-2.5 focus:border-[#0096c7] focus:outline-none transition-all"
          />
        </div>

        <div>
          <label className="text-[10px] font-black text-gray-400 uppercase mb-1 block">Descrição Detalhada</label>
          <textarea 
            rows={4}
            defaultValue={order.description}
            className="w-full border-2 border-[#ddd] rounded-md p-3 text-sm focus:border-[#0096c7] focus:outline-none transition-all resize-none"
          ></textarea>
        </div>

        <div className="bg-[#f9f9f9] p-4 rounded-xl border-2 border-[#ddd] space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-sm font-bold text-gray-600">Valor Total:</span>
            <span className="text-lg font-black text-[#0096c7]">
              R$ {order.value.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm font-bold text-gray-600">Pagamento:</span>
            <div className="flex items-center gap-2">
              <span className={`w-3 h-3 rounded-full ${order.paid ? 'bg-green-500' : 'bg-red-500'}`}></span>
              <span className="text-sm font-medium">{order.paid ? 'Confirmado' : 'Pendente'}</span>
            </div>
          </div>
        </div>
      </div>

      <div className="p-6 border-t-2 border-[#ddd] bg-[#f2f2f2] flex gap-3">
        <button className="flex-grow bg-[#0096c7] hover:bg-[#0077a3] text-white py-3 rounded-lg font-bold shadow-md transition-all active:scale-95">
          Salvar Alterações
        </button>
        <button onClick={onClose} className="px-6 py-3 border-2 border-[#ddd] bg-white rounded-lg text-gray-600 font-bold hover:bg-gray-50 transition-all">
          Sair
        </button>
      </div>
    </div>
  );
};

export default OSDetailSidebar;
