"use client";

import { createContext, useCallback, useContext, useState } from "react";

type Toast = { id: number; message: string; type: "success" | "error" | "info" };

const ToastContext = createContext<{ showToast: (message: string, type?: Toast["type"]) => void }>({
  showToast: () => {},
});

export function useToast() {
  return useContext(ToastContext);
}

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const showToast = useCallback((message: string, type: Toast["type"] = "success") => {
    const id = Date.now();
    setToasts((prev) => [...prev, { id, message, type }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 4000);
  }, []);

  const colorFor = (type: Toast["type"]) =>
    type === "success" ? "var(--success)" : type === "error" ? "var(--danger)" : "var(--ink)";

  return (
    <ToastContext.Provider value={{ showToast }}>
      {children}
      <div className="fixed bottom-4 right-4 z-50 space-y-2">
        {toasts.map((t) => (
          <div
            key={t.id}
            className="rounded-lg border px-4 py-2 text-sm shadow-lg"
            style={{
              background: "var(--paper-card)",
              borderColor: "var(--paper-border)",
              color: colorFor(t.type),
              minWidth: "220px",
            }}
          >
            {t.message}
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}