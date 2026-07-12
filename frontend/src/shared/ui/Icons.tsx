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
