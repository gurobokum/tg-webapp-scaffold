import { createInstance, KeyPrefix } from "i18next";
import resourcesToBackend from "i18next-resources-to-backend";
import { initReactI18next } from "react-i18next/initReactI18next";

import { fallbackLang, i18nOptions, Language, Namespace } from "./conf";

import { FallbackNs, UseTranslationOptions } from "react-i18next";

export type Options = UseTranslationOptions<KeyPrefix<FallbackNs<Namespace>>>;

// eslint-disable-next-line @typescript-eslint/no-unused-vars
const initI18next = async (lang: Language, ns: Namespace) => {
  const i18nInstance = createInstance();
  await i18nInstance
    .use(initReactI18next)
    .use(
      resourcesToBackend(
        (language: string, namespace: string) =>
          import(`./locales/${language}/${namespace}.yaml`)
      )
    )
    .init({
      ...i18nOptions,
      lng: lang,
      fallbackLng: fallbackLang,
    });
  return i18nInstance;
};

export async function getTranslation(
  lang: Language,
  ns: Namespace,
  options: Options = {}
) {
  const i18nextInstance = await initI18next(lang, ns);
  return {
    t: i18nextInstance.getFixedT(
      lang,
      Array.isArray(ns) ? ns[0] : ns,
      options.keyPrefix
    ),
    i18n: i18nextInstance,
  };
}
