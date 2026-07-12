import type { SVGProps } from 'react';

type IconProps = SVGProps<SVGSVGElement> & { size?: number };

function IconBase({ size = 22, children, ...props }: IconProps) {
  return (
    <svg
      aria-hidden="true"
      fill="none"
      height={size}
      viewBox="0 0 24 24"
      width={size}
      xmlns="http://www.w3.org/2000/svg"
      {...props}
    >
      {children}
    </svg>
  );
}

export function HomeIcon(props: IconProps) {
  return <IconBase {...props}><path d="M3 10.8 12 3l9 7.8v9.1a1.1 1.1 0 0 1-1.1 1.1h-5.2v-6.2H9.3V21H4.1A1.1 1.1 0 0 1 3 19.9v-9.1Z" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.8" /></IconBase>;
}

export function GridIcon(props: IconProps) {
  return <IconBase {...props}><path d="M4 4h6v6H4V4Zm10 0h6v6h-6V4ZM4 14h6v6H4v-6Zm10 0h6v6h-6v-6Z" stroke="currentColor" strokeLinejoin="round" strokeWidth="1.8" /></IconBase>;
}

export function BagIcon(props: IconProps) {
  return <IconBase {...props}><path d="M5.2 8.5h13.6l-.7 11.3H5.9L5.2 8.5Z" stroke="currentColor" strokeLinejoin="round" strokeWidth="1.8" /><path d="M8.7 9V6.8a3.3 3.3 0 1 1 6.6 0V9" stroke="currentColor" strokeLinecap="round" strokeWidth="1.8" /></IconBase>;
}

export function UserIcon(props: IconProps) {
  return <IconBase {...props}><circle cx="12" cy="8" r="3.4" stroke="currentColor" strokeWidth="1.8" /><path d="M5.5 20c.6-4 2.8-6 6.5-6s5.9 2 6.5 6" stroke="currentColor" strokeLinecap="round" strokeWidth="1.8" /></IconBase>;
}

export function SearchIcon(props: IconProps) {
  return <IconBase {...props}><circle cx="10.8" cy="10.8" r="6.3" stroke="currentColor" strokeWidth="1.8" /><path d="m16 16 4.2 4.2" stroke="currentColor" strokeLinecap="round" strokeWidth="1.8" /></IconBase>;
}

export function HeartIcon(props: IconProps) {
  return <IconBase {...props}><path d="M20.6 8.8c0 5-8.6 10.1-8.6 10.1S3.4 13.8 3.4 8.8A4.4 4.4 0 0 1 12 7.5a4.4 4.4 0 0 1 8.6 1.3Z" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.8" /></IconBase>;
}

export function ArrowRightIcon(props: IconProps) {
  return <IconBase {...props}><path d="M5 12h14m-5-5 5 5-5 5" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.8" /></IconBase>;
}

export function ChevronLeftIcon(props: IconProps) {
  return <IconBase {...props}><path d="m15 5-7 7 7 7" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.8" /></IconBase>;
}

export function SlidersIcon(props: IconProps) {
  return <IconBase {...props}><path d="M4 7h10m4 0h2M4 17h2m4 0h10M14 4v6M7 14v6" stroke="currentColor" strokeLinecap="round" strokeWidth="1.8" /></IconBase>;
}

export function SparklesIcon(props: IconProps) {
  return <IconBase {...props}><path d="m12 3 1.15 3.1L16 7.4l-2.85 1.25L12 12l-1.15-3.35L8 7.4l2.85-1.3L12 3Zm6 9 .85 2.1L21 15l-2.15.9L18 18l-.85-2.1L15 15l2.15-.9L18 12ZM6 13l1.1 2.9L10 17l-2.9 1.1L6 21l-1.1-2.9L2 17l2.9-1.1L6 13Z" fill="currentColor" /></IconBase>;
}

export function ShieldIcon(props: IconProps) {
  return <IconBase {...props}><path d="M12 3 5 6v5.2c0 4.3 2.5 7.6 7 9.8 4.5-2.2 7-5.5 7-9.8V6l-7-3Z" stroke="currentColor" strokeLinejoin="round" strokeWidth="1.8" /><path d="m8.9 12 2.1 2.1 4.4-4.4" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.8" /></IconBase>;
}

export function TruckIcon(props: IconProps) {
  return <IconBase {...props}><path d="M3 6h11v10H3V6Zm11 4h3.8L21 13.5V16h-7v-6Z" stroke="currentColor" strokeLinejoin="round" strokeWidth="1.8" /><circle cx="7" cy="18" r="2" stroke="currentColor" strokeWidth="1.8" /><circle cx="17" cy="18" r="2" stroke="currentColor" strokeWidth="1.8" /></IconBase>;
}

export function SettingsIcon(props: IconProps) {
  return <IconBase {...props}><circle cx="12" cy="12" r="3" stroke="currentColor" strokeWidth="1.8" /><path d="M19.4 15a1.7 1.7 0 0 0 .34 1.87l.06.06-2.12 2.12-.06-.06a1.7 1.7 0 0 0-1.87-.34 1.7 1.7 0 0 0-1 1.56V20.3h-3v-.09a1.7 1.7 0 0 0-1-1.56 1.7 1.7 0 0 0-1.87.34l-.06.06-2.12-2.12.06-.06A1.7 1.7 0 0 0 7.1 15a1.7 1.7 0 0 0-1.56-1H5.5v-3h.04a1.7 1.7 0 0 0 1.56-1 1.7 1.7 0 0 0-.34-1.87l-.06-.06 2.12-2.12.06.06a1.7 1.7 0 0 0 1.87.34 1.7 1.7 0 0 0 1-1.56V4.7h3v.09a1.7 1.7 0 0 0 1 1.56 1.7 1.7 0 0 0 1.87-.34l.06-.06 2.12 2.12-.06.06A1.7 1.7 0 0 0 19.4 10a1.7 1.7 0 0 0 1.56 1H21v3h-.04a1.7 1.7 0 0 0-1.56 1Z" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" /></IconBase>;
}

export function CheckIcon(props: IconProps) {
  return <IconBase {...props}><path d="m5 12.5 4.2 4.2L19 7" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" /></IconBase>;
}

export function CloseIcon(props: IconProps) {
  return <IconBase {...props}><path d="m6 6 12 12M18 6 6 18" stroke="currentColor" strokeLinecap="round" strokeWidth="1.8" /></IconBase>;
}
