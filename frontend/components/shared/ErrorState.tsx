import React from 'react';

export default function ErrorState({ message, onRetry }: { message: string, onRetry?: () => void }) {
  return (
    <div className="flex flex-col items-center justify-center p-8 bg-panelCharcoal border border-white/10 rounded-lg">
      <h3 className="text-textPrimary font-bold text-lg mb-2">Error</h3>
      <p className="text-textMuted mb-4">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="px-4 py-2 bg-neonBlue/10 text-neonBlue border border-neonBlue/20 rounded hover:bg-neonBlue/20 transition-colors"
        >
          Try Again
        </button>
      )}
    </div>
  );
}
