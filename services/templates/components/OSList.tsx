
import React from 'react';
import { ServiceOrder } from '../types';

interface OSListProps {
  orders: ServiceOrder[];
  isMobile: boolean;
  onSelectOrder: (os: ServiceOrder) => void;
}

const OSList: React.FC<OSListProps> = ({ orders, isMobile, onSelectOrder }) => {
  const totalValue = orders.reduce((acc, curr) => acc + curr.value, 0);

  const statusColors = {
    'Pendente': 'bg-sky-50 text-sky-700 border-sky-100',
    'Em Andamento': 'bg-amber-50 text-amber-700 border-amber-100',
    'Concluído': 'bg-emerald-50 text-emerald-700 border-emerald-100',
    'Cancelado': 'bg-rose-50 text-rose-700 border-rose-100'
  };

  if (isMobile) {
    return (
      <div className="space-y-4">
        {orders.map((os) => (
          <div 
            key={os.id} 
            onClick={() => onSelectOrder(os)}
            className="bg-white p-5 rounded-2xl shadow-sm border border-slate-200 active:scale-95 transition-all"
          >
            <div className="flex justify-between items-start mb-3">
              <div>
                <span className="text-[10px] font-black text-slate-400 uppercase mb-1 block">#{os.id} • {new Date(os.date).toLocaleDateString('pt-BR')}</span>
                <h3 className="font-black text-slate-800 leading-tight">{os.service}</h3>
              </div>
              <span className={`px-2 py-0.5 rounded-md text-[10px] font-black border uppercase ${statusColors[os.status]}`}>
                {os.status}
              </span>
            </div>
            <div className="flex justify-between items-end border-t border-slate-50 pt-3">
              <div className="text-xs text-slate-500">
                <i className="bi bi-person-fill mr-1"></i> {os.customer}
              </div>
              <div className="text-lg font-black text-emerald-600">
                R$ {os.value.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
              </div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="bg-white rounded-3xl shadow-xl border border-slate-200 overflow-hidden">
      <table className="w-full text-sm text-left border-collapse">
        <thead>
          <tr className="bg-slate-50/50 border-b border-slate-100">
            <th className="px-8 py-5 text-[10px] font-black text-slate-400 uppercase tracking-widest">Ordem / Projeto</th>
            <th className="px-8 py-5 text-[10px] font-black text-slate-400 uppercase tracking-widest text-center">Status</th>
            <th className="px-8 py-5 text-[10px] font-black text-slate-400 uppercase tracking-widest">Cliente</th>
            <th className="px-8 py-5 text-[10px] font-black text-slate-400 uppercase tracking-widest">Data</th>
            <th className="px-8 py-5 text-[10px] font-black text-slate-400 uppercase tracking-widest text-right">Valor Bruto</th>
            <th className="px-8 py-5 text-[10px] font-black text-slate-400 uppercase tracking-widest text-center">Ações</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {orders.map((os) => (
            <tr key={os.id} className="group hover:bg-slate-50/50 transition-all cursor-pointer" onClick={() => onSelectOrder(os)}>
              <td className="px-8 py-6">
                <div className="font-black text-slate-800 group-hover:text-emerald-600 transition-colors">#{os.id} {os.service}</div>
                <div className="text-[11px] text-slate-400 font-medium uppercase mt-1">{os.project || 'Serviço Geral'}</div>
              </td>
              <td className="px-8 py-6">
                <div className="flex justify-center">
                  <span className={`px-3 py-1 rounded-lg text-[10px] font-black border uppercase ${statusColors[os.status]}`}>
                    {os.status}
                  </span>
                </div>
              </td>
              <td className="px-8 py-6">
                <div className="font-bold text-slate-700">{os.customer}</div>
                <div className="text-[11px] text-slate-400 italic">Cliente cadastrado</div>
              </td>
              <td className="px-8 py-6">
                <div className="font-mono text-xs text-slate-600 bg-slate-100 inline-block px-2 py-1 rounded-md">
                  {new Date(os.date).toLocaleDateString('pt-BR')}
                </div>
              </td>
              <td className="px-8 py-6 text-right font-black text-slate-800 text-base">
                R$ {os.value.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
              </td>
              <td className="px-8 py-6 text-center">
                <button className="w-10 h-10 bg-white border border-slate-200 rounded-xl text-slate-400 group-hover:border-emerald-500 group-hover:text-emerald-600 shadow-sm transition-all hover:scale-110 active:scale-95">
                  <i className="bi bi-eye-fill"></i>
                </button>
              </td>
            </tr>
          ))}
        </tbody>
        <tfoot className="bg-slate-50/80 border-t-2 border-slate-100">
          <tr>
            <td colSpan={4} className="px-8 py-8 text-right font-black text-slate-400 uppercase text-[10px] tracking-widest">Total Geral da Seleção</td>
            <td className="px-8 py-8 text-right text-3xl font-black text-emerald-600">
              R$ {totalValue.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
            </td>
            <td></td>
          </tr>
        </tfoot>
      </table>
    </div>
  );
};

export default OSList;
