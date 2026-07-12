import { Link } from '../router';
export function SectionHeader({ title, link, linkLabel = 'Дивитися всі' }: { title: string; link?: string; linkLabel?: string }) { return <div className="section-header"><h2>{title}</h2>{link ? <Link to={link}>{linkLabel}</Link> : null}</div>; }
