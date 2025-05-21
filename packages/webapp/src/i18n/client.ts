"use client";

import { useEffect } from "react";
import i18next from "i18next";
import {
  initReactI18next,
  useTranslation as useTranslationOrg,
} from "react-i18next";
import resourcesToBackend from "i18next-resources-to-backend";
import LanguageDetector from "i18next-browser-languagedetector";

import { getCookie } from "cookies-next";

import {
  cookieName,
  i18nOptions,
  Language,
  languages,
  Namespace,
} from "./conf";
import { Options } from ".";
import { getLang } from "./utils";

const isServer = typeof window === "undefined";

i18next
  .use(initReactI18next)
  .use(LanguageDetector)
  .use(
    resourcesToBackend(
      (language: Language, namespace: Namespace) =>
        import(`./locales/${language}/${namespace}.yaml`)
    )
  )
  .init({
    ...i18nOptions,
    lng: undefined, // let detect the language on client side
    detection: {
      order: ["path", "htmlTag", "cookie", "navigator"],
    },
    preload: isServer ? languages : [],
  });

export function useTranslation(
  _lang: Language,
  ns: Namespace,
  options: Options = {}
) {
  const ret = useTranslationOrg(ns, options);
  const { i18n } = ret;
  const lang = getLang(getCookie(cookieName) as string | undefined);

  useEffect(() => {
    if (i18n.resolvedLanguage !== lang) {
      i18n.changeLanguage(lang);
    }
  }, [lang, i18n]);

  return ret;
}
