import * as React from "react";

type InputProps = React.InputHTMLAttributes<HTMLInputElement>;

export function Input({ className = "", ...props }: InputProps) {
  return (
    <input
      className={`flex w-full rounded-lg border-2 border-gray-300 bg-white px-4 py-3 text-base text-gray-900 placeholder:text-gray-400 focus:border-gray-900 focus:outline-none disabled:cursor-not-allowed disabled:opacity-50 ${className}`}
      {...props}
    />
  );
}
