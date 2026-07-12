/** @param {string|number} value @param {string} [currency] */
export function formatCatalogPrice(value, currency = 'UAH') {
  const numeric = Number(value);
  if (!Number.isFinite(numeric)) return '—';
  return new Intl.NumberFormat('uk-UA', {
    style: 'currency',
    currency,
    maximumFractionDigits: 0,
  }).format(numeric);
}

/** @param {string|number|null|undefined} price @param {string|number|null|undefined} compareAt */
export function calculateDiscount(price, compareAt) {
  const current = Number(price);
  const previous = Number(compareAt);
  if (!Number.isFinite(current) || !Number.isFinite(previous) || previous <= current || previous <= 0) return null;
  return Math.round(((previous - current) / previous) * 100);
}

/** @param {Array<{color_code:string,size_code:string,is_available:boolean}>} variants @param {string|null} colorCode */
export function availableSizeCodes(variants, colorCode) {
  if (!colorCode) return [];
  return variants.filter((variant) => variant.color_code === colorCode && variant.is_available).map((variant) => variant.size_code);
}

/** @param {Array<{color_code:string,size_code:string}>} variants @param {string|null} colorCode @param {string|null} sizeCode */
export function findVariant(variants, colorCode, sizeCode) {
  if (!colorCode || !sizeCode) return null;
  return variants.find((variant) => variant.color_code === colorCode && variant.size_code === sizeCode) || null;
}

/** @param {URLSearchParams} params */
export function countActiveCatalogFilters(params) {
  const keys = ['category','brand','color','size','min_price','max_price','only_available','sale','new'];
  return keys.filter((key) => params.has(key) && params.get(key) !== 'false').length;
}

/** @param {{is_admin?:boolean}|null|undefined} user */
export function canAccessAdmin(user) {
  return Boolean(user?.is_admin);
}
