export function formatCurrency(value: number): string {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(value);
}

export function formatPercentage(value: number | null | undefined): string {
  if (value === null || value === undefined) return "N/A";
  
  // If the value is a ratio (e.g. 0.1234), multiply by 100
  const pct = Math.abs(value) < 1.0 && value !== 0 ? value * 100 : value;
  return `${pct > 0 ? "+" : ""}${pct.toFixed(2)}%`;
}

export function formatDate(dateString: string | null | undefined): string {
  if (!dateString) return "N/A";
  try {
    const d = new Date(dateString);
    if (isNaN(d.getTime())) return dateString;
    return d.toLocaleDateString("en-IN", {
      day: "2-digit",
      month: "short",
      year: "numeric",
    });
  } catch {
    return dateString;
  }
}

export function cn(...inputs: Array<string | undefined | null | false>): string {
  return inputs.filter(Boolean).join(" ");
}
