export type PreviewProduct = {
  id: string;
  title: string;
  category: string;
  price: number;
  oldPrice?: number;
  image: string;
  badge?: 'NEW' | 'SALE' | 'LIMITED';
  colors: string[];
};

export const previewCategories = [
  { id: 'new', label: 'Новинки' },
  { id: 'women', label: 'Жінкам' },
  { id: 'men', label: 'Чоловікам' },
  { id: 'shoes', label: 'Взуття' },
  { id: 'accessories', label: 'Аксесуари' },
];

export const previewProducts: PreviewProduct[] = [
  {
    id: 'p1',
    title: 'Структурований тренч Oslo',
    category: 'Верхній одяг',
    price: 4290,
    oldPrice: 4990,
    image: '/mock/trench.svg',
    badge: 'NEW',
    colors: ['#21304a', '#d9d0c2'],
  },
  {
    id: 'p2',
    title: 'Кросівки Motion 02',
    category: 'Взуття',
    price: 3190,
    image: '/mock/sneakers.svg',
    badge: 'LIMITED',
    colors: ['#f5f5f3', '#1b2550'],
  },
  {
    id: 'p3',
    title: 'Сукня-сорочка Linea',
    category: 'Сукні',
    price: 2790,
    image: '/mock/dress.svg',
    badge: 'NEW',
    colors: ['#1d3a73', '#ded7cb'],
  },
  {
    id: 'p4',
    title: 'Сумка City Mini',
    category: 'Аксесуари',
    price: 1990,
    oldPrice: 2390,
    image: '/mock/bag.svg',
    badge: 'SALE',
    colors: ['#131c2f', '#b8a78f'],
  },
  {
    id: 'p5',
    title: 'Худі Essential Form',
    category: 'Світшоти',
    price: 2290,
    image: '/mock/hoodie.svg',
    colors: ['#d9dde5', '#2a3b6b'],
  },
  {
    id: 'p6',
    title: 'Бомбер Studio 26',
    category: 'Куртки',
    price: 3590,
    image: '/mock/bomber.svg',
    badge: 'NEW',
    colors: ['#194bc4', '#252a33'],
  },
];

export function formatPrice(value: number): string {
  return new Intl.NumberFormat('uk-UA').format(value) + ' ₴';
}
