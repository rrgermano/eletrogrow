
import React, { useState } from 'react';
import { GoogleGenAI } from "@google/genai";
import { ServiceOrder } from '../types';

interface AIAssistantProps {
  orders: ServiceOrder[];
}

const AIAssistant: React.FC<AIAssistantProps> = ({ orders }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [insight, setInsight] = useState<string | null>(null);

  const analyzeOrders = async () => {
    setLoading(true);
    setInsight(null);
    try {
      const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });
      const prompt = `
        Analise a seguinte lista de Ordens de Serviço de um ERP e forneça um resumo executivo rápido em português:
        ${JSON.stringify(orders.map(o => ({ s: o.service, v: o.value, st: o.status, d: o.date })))}
        
        Identifique:
        1. Faturamento total.
        2. Status crítico (muitas pendentes?).
        3. Destaque para o maior valor.
        Mantenha o tom profissional e direto.
      `;

      const response = await ai.models.generateContent({
        model: 'gemini-3-flash-preview',
        contents: prompt,
      });

      setInsight(response.text);
    } catch (error) {
      setInsight("Desculpe, não consegui analisar os dados agora.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed bottom-6 right-6 z-50">
      {isOpen && (
        <div className="absolute bottom-16 right-0 w-80 bg-white rounded-2xl shadow-2xl border border-emerald-100 overflow-hidden flex flex-col animate-in fade-in slide-in-from-bottom-4 duration-300">
          <div className="bg-emerald-600 p-4 text-white flex justify-between items-center">
            <span className="font-bold flex items-center gap-2">
              <i className="bi bi-robot"></i> Assistente EG AI
            </span>
            <button onClick={() => setIsOpen(false)}><i className="bi bi-x-lg"></i></button>
          </div>
          <div className="p-4 max-h-96 overflow-y-auto bg-gray-50 min-h-[150px]">
            {loading ? (
              <div className="flex flex-col items-center justify-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-600"></div>
                <p className="mt-2 text-xs text-gray-500">Analisando ordens...</p>
              </div>
            ) : insight ? (
              <div className="text-sm text-gray-700 leading-relaxed whitespace-pre-wrap italic">
                {insight}
              </div>
            ) : (
              <div className="text-center py-4">
                <p className="text-sm text-gray-500">Clique abaixo para analisar o status atual do seu serviço.</p>
              </div>
            )}
          </div>
          <div className="p-4 border-t border-gray-100">
            <button
              onClick={analyzeOrders}
              disabled={loading}
              className="w-full bg-emerald-600 hover:bg-emerald-700 text-white py-2 rounded-lg text-sm font-bold transition-all disabled:opacity-50"
            >
              Gerar Relatório IA
            </button>
          </div>
        </div>
      )}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-14 h-14 bg-emerald-600 text-white rounded-full shadow-lg hover:scale-110 active:scale-95 transition-all flex items-center justify-center text-2xl"
      >
        <i className={`bi ${isOpen ? 'bi-x-lg' : 'bi-chat-dots-fill'}`}></i>
      </button>
    </div>
  );
};

export default AIAssistant;
