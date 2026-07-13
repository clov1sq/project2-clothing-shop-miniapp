import type { SVGProps } from 'react';

type IconProps = SVGProps<SVGSVGElement> & { size?: number };

function IconBase({ size = 22, children, ...props }: IconProps) {
  return <svg viewBox="0 0 24 24" width={size} height={size} fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" {...props}>{children}</svg>;
}

export const HomeIcon = (props: IconProps) => <IconBase {...props}><path d="m3 10 9-7 9 7"/><path d="M5 9v11h14V9"/><path d="M9 20v-6h6v6"/></IconBase>;
export const GridIcon = (props: IconProps) => <IconBase {...props}><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></IconBase>;
export const UserIcon = (props: IconProps) => <IconBase {...props}><circle cx="12" cy="8" r="4"/><path d="M4.5 21a7.5 7.5 0 0 1 15 0"/></IconBase>;
export const SearchIcon = (props: IconProps) => <IconBase {...props}><circle cx="11" cy="11" r="7"/><path d="m20 20-4-4"/></IconBase>;
export const FilterIcon = (props: IconProps) => <IconBase {...props}><path d="M4 7h16M7 12h10M10 17h4"/></IconBase>;
export const SortIcon = (props: IconProps) => <IconBase {...props}><path d="M8 6h12M8 12h8M8 18h4"/><path d="m4 4 0 16"/></IconBase>;
export const ArrowLeftIcon = (props: IconProps) => <IconBase {...props}><path d="m15 18-6-6 6-6"/></IconBase>;
export const ArrowRightIcon = (props: IconProps) => <IconBase {...props}><path d="m9 18 6-6-6-6"/></IconBase>;
export const CloseIcon = (props: IconProps) => <IconBase {...props}><path d="M6 6l12 12M18 6 6 18"/></IconBase>;
export const ChevronDownIcon = (props: IconProps) => <IconBase {...props}><path d="m6 9 6 6 6-6"/></IconBase>;
export const CheckIcon = (props: IconProps) => <IconBase {...props}><path d="m5 12 4 4L19 6"/></IconBase>;
export const PlusIcon = (props: IconProps) => <IconBase {...props}><path d="M12 5v14M5 12h14"/></IconBase>;
export const EditIcon = (props: IconProps) => <IconBase {...props}><path d="m4 20 4.5-1 10-10a2.1 2.1 0 0 0-3-3l-10 10L4 20Z"/><path d="m14 7 3 3"/></IconBase>;
export const BoxIcon = (props: IconProps) => <IconBase {...props}><path d="m4 7 8-4 8 4-8 4-8-4Z"/><path d="m4 7v10l8 4 8-4V7"/><path d="M12 11v10"/></IconBase>;
export const ImageIcon = (props: IconProps) => <IconBase {...props}><rect x="3" y="4" width="18" height="16" rx="2"/><circle cx="8.5" cy="9" r="1.5"/><path d="m21 15-5-5L5 20"/></IconBase>;
export const ShieldIcon = (props: IconProps) => <IconBase {...props}><path d="M12 3 4.5 6v5.5c0 4.6 3.1 7.6 7.5 9.5 4.4-1.9 7.5-4.9 7.5-9.5V6L12 3Z"/><path d="m9 12 2 2 4-4"/></IconBase>;
export const HeartIcon = ({ filled = false, ...props }: IconProps & { filled?: boolean }) => <IconBase {...props} fill={filled ? 'currentColor' : 'none'}><path d="M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.6l-1-1a5.5 5.5 0 0 0-7.8 7.8l1 1L12 21l7.8-7.6 1-1a5.5 5.5 0 0 0 0-7.8Z"/></IconBase>;
export const CartIcon = (props: IconProps) => <IconBase {...props}><path d="M3 4h2l2.1 10.2a2 2 0 0 0 2 1.6h7.8a2 2 0 0 0 2-1.6L20.2 8H6"/><circle cx="9" cy="20" r="1"/><circle cx="17" cy="20" r="1"/></IconBase>;
export const TrashIcon = (props: IconProps) => <IconBase {...props}><path d="M4 7h16M9 7V4h6v3M7 7l1 13h8l1-13"/><path d="M10 11v5M14 11v5"/></IconBase>;
export const MinusIcon = (props: IconProps) => <IconBase {...props}><path d="M5 12h14"/></IconBase>;
export const WifiOffIcon = (props: IconProps) => <IconBase {...props}><path d="m2 2 20 20M8.5 8.5A8 8 0 0 1 20 10M5 10a11 11 0 0 1 1.2-.9M8.5 14.5a5 5 0 0 1 7 0M12 19h.01"/></IconBase>;
export const MapPinIcon = (props: IconProps) => <IconBase {...props}><path d="M20 10c0 5-8 11-8 11S4 15 4 10a8 8 0 1 1 16 0Z"/><circle cx="12" cy="10" r="2.5"/></IconBase>;
export const PhoneIcon = (props: IconProps) => <IconBase {...props}><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.4 19.4 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 2 .7 2.9a2 2 0 0 1-.5 2.1L8 10a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.5c.9.3 1.9.6 2.9.7A2 2 0 0 1 22 16.9Z"/></IconBase>;
export const ClockIcon = (props: IconProps) => <IconBase {...props}><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></IconBase>;
export const CheckCircleIcon = (props: IconProps) => <IconBase {...props}><circle cx="12" cy="12" r="9"/><path d="m8 12 2.5 2.5L16 9"/></IconBase>;
