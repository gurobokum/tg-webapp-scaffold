import { fallbackLang } from "./conf";

export function getLang(languageCode?: string) {
  switch (languageCode) {
    case "ru":
    case "kz":
    case "uk":
      return "ru";
    case "en":
      return "en";
    default:
      return fallbackLang;
  }
}
