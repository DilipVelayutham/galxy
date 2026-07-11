// components/ui/LoadingSkeleton.tsx

type Props = {
  height?: string;
  width?: string;
  className?: string;
};

export const LoadingSkeleton = ({ height = '1rem', width = '100%', className = '' }: Props) => {
  return (
    <div
      role="status"
      aria-label="Loading…"
      style={{ height, width }}
      className={[
        'rounded bg-panelCharcoal',
        'relative overflow-hidden',
        'before:absolute before:inset-0',
        'before:bg-gradient-to-r before:from-transparent before:via-textMuted/10 before:to-transparent',
        'before:animate-[shimmer_1.5s_infinite]',
        className,
      ].join(' ')}
    />
  );
};
