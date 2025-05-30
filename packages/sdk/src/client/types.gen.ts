// This file is auto-generated by @hey-api/openapi-ts

export type BuyCreditsRequest = {
  package_name: string;
};

export type CreditsPackage = {
  package_name: string;
  credits_amount: number;
  stars_amount: number;
};

export type HttpForbiddenError = {
  detail: string;
  status_code: number;
};

export type HttpUnauthorizedError = {
  detail: string;
  status_code: number;
};

export type HttpValidationError = {
  detail?: Array<ValidationError>;
};

export type TgUser = {
  tg_id: number;
  username?: string;
  first_name?: string;
  last_name?: string;
  language_code?: string;
  is_bot?: boolean;
  is_admin?: boolean;
  credits_balance: number;
};

export type ValidationError = {
  loc: Array<string | number>;
  msg: string;
  type: string;
};

export type AuthMeData = {
  body?: never;
  path?: never;
  query?: never;
  url: "/tgbot/auth/";
};

export type AuthMeResponses = {
  /**
   * Successful Response
   */
  200: TgUser;
};

export type AuthMeResponse = AuthMeResponses[keyof AuthMeResponses];

export type PostWebhookData = {
  body?: never;
  path?: never;
  query?: never;
  url: "/tgbot/webhook";
};

export type PostWebhookErrors = {
  /**
   * Forbidden
   */
  403: HttpForbiddenError;
};

export type PostWebhookError = PostWebhookErrors[keyof PostWebhookErrors];

export type PostWebhookResponses = {
  /**
   * Successful Response
   */
  200: unknown;
};

export type TgCreditsListPackagesData = {
  body?: never;
  path?: never;
  query?: never;
  url: "/credits/packages";
};

export type TgCreditsListPackagesErrors = {
  /**
   * Unauthorized
   */
  401: HttpUnauthorizedError;
};

export type TgCreditsListPackagesError =
  TgCreditsListPackagesErrors[keyof TgCreditsListPackagesErrors];

export type TgCreditsListPackagesResponses = {
  /**
   * Successful Response
   */
  200: Array<CreditsPackage>;
};

export type TgCreditsListPackagesResponse =
  TgCreditsListPackagesResponses[keyof TgCreditsListPackagesResponses];

export type TgCreditsSendInvoiceData = {
  body: BuyCreditsRequest;
  path?: never;
  query?: never;
  url: "/credits/send_invoice";
};

export type TgCreditsSendInvoiceErrors = {
  /**
   * Unauthorized
   */
  401: HttpUnauthorizedError;
  /**
   * Validation Error
   */
  422: HttpValidationError;
};

export type TgCreditsSendInvoiceError =
  TgCreditsSendInvoiceErrors[keyof TgCreditsSendInvoiceErrors];

export type TgCreditsSendInvoiceResponses = {
  /**
   * Successful Response
   */
  200: unknown;
};

export type RootData = {
  body?: never;
  path?: never;
  query?: never;
  url: "/";
};

export type RootResponses = {
  /**
   * Successful Response
   */
  200: {
    [key: string]: string;
  };
};

export type RootResponse = RootResponses[keyof RootResponses];

export type ClientOptions = {
  baseUrl: `${string}://${string}` | (string & {});
};
