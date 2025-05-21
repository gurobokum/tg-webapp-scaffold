import { HttpForbiddenError, HttpValidationError } from "@tg-webapp/sdk";

export class AppError extends Error {}

export class UnauthenticatedError extends AppError {}

export function strError(
  error: HttpForbiddenError | HttpValidationError
): string {
  if (error.detail && Array.isArray(error.detail)) {
    return error.detail.map((e) => e.msg).join(", ");
  }
  return error.detail || "Unknown error";
}
