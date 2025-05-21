export const languages = ["ru", "en"] as const;
export const fallbackLang = "ru";
export const namespaces = ["app", "components"] as const;
export const cookieName = "tg_webapp_lang";

export type Language = (typeof languages)[number];
export type Namespace = (typeof namespaces)[number];

export const i18nOptions = {
  supportedLngs: languages,
  ns: ["app", "components"],
  defaultNS: "app",
  interpolation: {
    escapeValue: false,
  },
};
