import { cn } from '@/lib/utils';

interface AxLogoProps {
  name: string;
  operator: string;
  className?: string;
}

/** Text logo: "AX" in the brand teal followed by the service name, like the maru2-dx.com logo */
export function AxLogo({ name, operator, className }: AxLogoProps) {
  return (
    <span className={cn('inline-flex flex-col leading-none', className)}>
      <span className="flex items-baseline gap-1">
        <span className="font-ax-latin text-2xl font-black tracking-tight text-ax-teal-dark">
          AX
        </span>
        <span className="text-lg font-bold text-ax-ink">{name}</span>
      </span>
      <span className="mt-1 text-[11px] font-medium text-gray-600">{operator}</span>
    </span>
  );
}
