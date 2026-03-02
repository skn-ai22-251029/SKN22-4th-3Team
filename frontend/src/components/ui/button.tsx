import * as React from "react";

type ButtonProps = React.ButtonHTMLAttributes<HTMLButtonElement>;

export function Button({ className = "", children, ...props }: ButtonProps) {
  return (
    <button
      className={`inline-flex items-center justify-center rounded-lg font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-gray-900 disabled:pointer-events-none disabled:opacity-50 ${className}`}
      {...props}
    >
      {children}
    </button>
  );
}
