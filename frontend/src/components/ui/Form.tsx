import type { InputHTMLAttributes, ReactNode, SelectHTMLAttributes, TextareaHTMLAttributes } from "react";
import clsx from "clsx";

const fieldBase =
  "w-full rounded-lg border border-(--color-border-strong) bg-white/[0.03] px-3 py-2.5 text-sm text-ink placeholder:text-ink-muted transition-colors focus:border-brand-2/60 focus:outline-none focus:ring-2 focus:ring-brand-2/20";

export function FieldShell({
  label,
  error,
  hint,
  required,
  children,
}: {
  label?: string;
  error?: string;
  hint?: string;
  required?: boolean;
  children: ReactNode;
}) {
  return (
    <label className="flex flex-col gap-1.5 text-sm">
      {label && (
        <span className="font-medium text-ink-secondary">
          {label}
          {required && <span className="text-critical"> *</span>}
        </span>
      )}
      {children}
      {error ? (
        <span className="text-xs text-critical">{error}</span>
      ) : hint ? (
        <span className="text-xs text-ink-muted">{hint}</span>
      ) : null}
    </label>
  );
}

interface InputFieldProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  hint?: string;
}

export function InputField({ label, error, hint, required, className, ...rest }: InputFieldProps) {
  return (
    <FieldShell label={label} error={error} hint={hint} required={required}>
      <input className={clsx(fieldBase, className)} required={required} {...rest} />
    </FieldShell>
  );
}

interface TextareaFieldProps extends TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  error?: string;
  hint?: string;
}

export function TextareaField({ label, error, hint, required, className, ...rest }: TextareaFieldProps) {
  return (
    <FieldShell label={label} error={error} hint={hint} required={required}>
      <textarea className={clsx(fieldBase, "min-h-24 resize-y", className)} required={required} {...rest} />
    </FieldShell>
  );
}

interface SelectFieldProps extends SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  error?: string;
  hint?: string;
}

export function SelectField({ label, error, hint, required, className, children, ...rest }: SelectFieldProps) {
  return (
    <FieldShell label={label} error={error} hint={hint} required={required}>
      <select className={clsx(fieldBase, "appearance-none", className)} required={required} {...rest}>
        {children}
      </select>
    </FieldShell>
  );
}
