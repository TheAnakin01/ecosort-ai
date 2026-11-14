import type { MaterialCommunityIcons } from '@expo/vector-icons';

import type { Category } from './types';

type IconName = keyof typeof MaterialCommunityIcons.glyphMap;

export type CategoryInfo = {
  label: string;
  color: string;
  soft: string;
  icon: IconName;
  bin: string;
  examples: string;
  mistakes: string[];
};

export const CATEGORIES: Category[] = ['paper', 'plastic', 'metal', 'organic'];

export const CATEGORY_INFO: Record<Category, CategoryInfo> = {
  paper: {
    label: 'Paper',
    color: '#1D6FB8',
    soft: '#E6F0FA',
    icon: 'newspaper-variant-outline',
    bin: 'Dry waste',
    examples: 'Newspaper, cardboard boxes, paper sheets, paper packaging',
    mistakes: [
      'Greasy pizza boxes and used tissues are not clean paper. They go with wet waste.',
      'Paper cups often have a plastic lining, so they are not plain paper.',
    ],
  },
  plastic: {
    label: 'Plastic',
    color: '#B45F06',
    soft: '#FBEFDF',
    icon: 'bottle-soda-outline',
    bin: 'Dry waste',
    examples: 'Bottles, containers, wrappers, plastic packaging',
    mistakes: [
      'Bottles with liquid or food left inside spoil the rest of the dry waste. Empty and rinse them.',
      'Chip packets and other shiny wrappers mix plastic and foil, and many recyclers do not take them.',
    ],
  },
  metal: {
    label: 'Metal',
    color: '#5B4BB5',
    soft: '#ECE9FA',
    icon: 'nut',
    bin: 'Dry waste',
    examples: 'Drink cans, food tins, metal containers, foil',
    mistakes: [
      'Tins with food left in them attract pests. Rinse them first.',
      'Batteries are not ordinary metal waste. They need a separate e-waste drop-off.',
    ],
  },
  organic: {
    label: 'Organic',
    color: '#2E7D32',
    soft: '#E6F3E7',
    icon: 'food-apple-outline',
    bin: 'Wet waste',
    examples: 'Fruit peels, vegetable scraps, leftover food, leaves',
    mistakes: [
      'Food thrown away inside a plastic bag cannot be composted. Empty the bag into wet waste.',
      'Mixing wet waste into dry waste makes paper and cardboard unusable.',
    ],
  },
};
