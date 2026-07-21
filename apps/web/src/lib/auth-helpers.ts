export function getAccountType(): "personal" | "company" | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("account_type") as "personal" | "company" | null;
}