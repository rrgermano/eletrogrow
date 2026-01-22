
import { ServiceOrder } from './types';

export const MOCK_ORDERS: ServiceOrder[] = [
  {
    id: 1,
    customer: "João Silva",
    service: "Manutenção de Ar Condicionado",
    description: "Limpeza completa e troca de filtros",
    date: new Date().toISOString().split('T')[0],
    value: 250.00,
    status: 'Concluído',
    project: "Residencial",
    favored: "Clima Tech",
    payment_method: "Pix",
    paid: true,
    closing: true
  },
  {
    id: 2,
    customer: "Maria Oliveira",
    service: "Instalação Elétrica",
    description: "Novos pontos de tomada na cozinha",
    date: new Date(Date.now() + 86400000).toISOString().split('T')[0],
    value: 480.00,
    status: 'Pendente',
    project: "Reforma AP 402",
    favored: "Eletro Solution",
    payment_method: "Cartão",
    paid: false,
    closing: false
  },
  {
    id: 3,
    customer: "Condomínio Solar",
    service: "Pintura de Fachada",
    description: "Pintura externa bloco A",
    date: new Date(Date.now() + 172800000).toISOString().split('T')[0],
    value: 12500.00,
    status: 'Em Andamento',
    project: "Manutenção Condominial",
    favored: "Tintas & Cia",
    payment_method: "Boleto",
    paid: true,
    closing: false
  },
  {
    id: 4,
    customer: "Tech Solutions",
    service: "Reparo de Servidor",
    description: "Troca de fonte redundante",
    date: new Date(Date.now() - 86400000).toISOString().split('T')[0],
    value: 890.00,
    status: 'Concluído',
    project: "Infra TI",
    favored: "Dell Brasil",
    payment_method: "Transferência",
    paid: true,
    closing: true
  },
  {
    id: 5,
    customer: "Sônia Ramos",
    service: "Jardinagem",
    description: "Poda de árvores e adubação",
    date: new Date().toISOString().split('T')[0],
    value: 150.00,
    status: 'Pendente',
    project: "Manutenção Mensal",
    favored: "Verde Vida",
    payment_method: "Dinheiro",
    paid: false,
    closing: false
  }
];
