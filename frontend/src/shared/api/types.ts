export type User = {
  id: string;
  telegram_id: number;
  username: string | null;
  first_name: string;
  last_name: string | null;
  display_name: string;
  role: 'owner' | 'admin' | null;
  is_admin: boolean;
};

export type Category = {
  id: string;
  parent_id: string | null;
  name: string;
  slug: string;
  description: string | null;
  image_url: string | null;
  sort_order: number;
  is_active: boolean;
};

export type Brand = {
  id: string;
  name: string;
  slug: string;
  description: string | null;
  logo_url: string | null;
  is_active: boolean;
};

export type CatalogColor = {
  id?: string;
  name: string;
  code: string;
  hex_value: string | null;
  sort_order?: number;
  is_active?: boolean;
};

export type CatalogSize = {
  id?: string;
  name: string;
  code: string;
  sort_order?: number;
  is_active?: boolean;
};

export type ProductCardData = {
  id: string;
  slug: string;
  brand: { name: string; slug: string };
  category: { name: string; slug: string };
  name: string;
  model_code: string;
  short_description: string | null;
  price: string;
  compare_at_price: string | null;
  discount_percent: number | null;
  currency: string;
  image_url: string | null;
  thumbnail_url: string | null;
  is_new: boolean;
  is_featured: boolean;
  is_sale: boolean;
  is_available: boolean;
  colors: CatalogColor[];
};

export type ProductMedia = {
  id: string;
  variant_id: string | null;
  url: string;
  thumbnail_url: string | null;
  alt_text: string | null;
  sort_order: number;
  is_primary: boolean;
};

export type ProductVariant = {
  id: string;
  color_id: string;
  size_id: string;
  color_code: string;
  size_code: string;
  sku: string;
  barcode: string | null;
  price: string;
  compare_at_price: string | null;
  discount_percent: number | null;
  available_quantity: number;
  quantity_on_hand?: number;
  quantity_reserved?: number;
  is_available: boolean;
  is_active: boolean;
  archived_at: string | null;
};

export type ProductDetailData = ProductCardData & {
  description: string | null;
  material: string | null;
  care_instructions: string | null;
  status: 'draft' | 'active' | 'archived';
  version: number | null;
  published_at: string | null;
  archived_at: string | null;
  media: ProductMedia[];
  colors: CatalogColor[];
  sizes: CatalogSize[];
  variants: ProductVariant[];
};

export type Pagination = {
  page: number;
  limit: number;
  total: number;
  pages?: number;
  has_next?: boolean;
};

export type CatalogResponse = { items: ProductCardData[]; pagination: Pagination };

export type HomeResponse = {
  categories: Category[];
  new_products: ProductCardData[];
  sale_products: ProductCardData[];
  featured_products: ProductCardData[];
};

export type CatalogMeta = {
  categories: Category[];
  brands: Brand[];
  colors: CatalogColor[];
  sizes: CatalogSize[];
  sorts: string[];
};

export type ApiErrorPayload = {
  code: string;
  message: string;
  details?: Record<string, unknown>;
};
