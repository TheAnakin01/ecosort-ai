import type { Category } from './types';

export const CATEGORIES: Category[] = ['paper', 'plastic', 'metal', 'organic'];

export const CATEGORY_INFO: Record<Category, { label: string; color: string; examples: string }> = {
  paper: { label: 'Paper', color: '#1D6FB8', examples: 'Newspaper, cardboard, paper packaging' },
  plastic: { label: 'Plastic', color: '#B45F06', examples: 'Bottles, containers, wrappers' },
  metal: { label: 'Metal', color: '#5B4BB5', examples: 'Cans, tins, foil' },
  organic: { label: 'Organic', color: '#2E7D32', examples: 'Peels, food scraps, leaves' },
};

export const theme = {
  brand: '#1B6B4A',
  brandSoft: '#E4F2EB',
  background: '#F6F8F6',
  card: '#FFFFFF',
  text: '#16211C',
  muted: '#5C6B63',
  border: '#D9E2DC',
  danger: '#B3261E',
  dangerSoft: '#FCEEED',
  warning: '#8A5A00',
  warningSoft: '#FFF4DC',
};
