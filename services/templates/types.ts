
export type OSStatus = 'Pendente' | 'Em Andamento' | 'Concluído' | 'Cancelado';

export interface ServiceOrder {
  id: number;
  customer: string;
  service: string;
  description: string;
  date: string; // ISO format YYYY-MM-DD
  value: number;
  status: OSStatus;
  project?: string;
  favored?: string;
  payment_method?: string;
  paid: boolean;
  closing: boolean;
}

export type ViewType = 'list' | 'calendar';

export interface DashboardStats {
  totalValue: number;
  pendingCount: number;
  completedCount: number;
  ongoingCount: number;
}
