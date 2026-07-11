import { useRef, useCallback, useEffect } from 'react';

/**
 * A type-safe debounce hook that wraps a callback and delays its execution.
 * Includes a manual cancel() method and automatic cleanup on component unmount.
 */
export function useDebouncedCallback<Args extends unknown[], Return>(
  callback: (...args: Args) => Return,
  delay: number
): ((...args: Args) => void) & { cancel: () => void } {
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);
  const callbackRef = useRef(callback);

  // Keep callback reference updated without re-triggering effects
  useEffect(() => {
    callbackRef.current = callback;
  }, [callback]);

  const debouncedFn = useCallback(
    (...args: Args) => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }

      timeoutRef.current = setTimeout(() => {
        callbackRef.current(...args);
      }, delay);
    },
    [delay]
  );

  const cancel = useCallback(() => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
    }
  }, []);

  // Clear timeout automatically when the component unmounts
  useEffect(() => {
    return cancel;
  }, [cancel]);

  return Object.assign(debouncedFn, { cancel });
}
