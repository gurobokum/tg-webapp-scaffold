"use client";

import { createContext, useCallback, useState } from "react";
import Script from "next/script";
import type { WebApp } from "telegram";
import { settings } from "@/conf";
import mockWebApp from "@/utils/mockWebApp";

const TELEGRAM_SCRIPT_URL = "https://telegram.org/js/telegram-web-app.js";

export const WebAppContext = createContext<WebApp | null>(null);

export const parseTGUserData = (initData?: string) => {
  if (!initData) {
    return {};
  }
  const chunks = initData.split("&");
  const userRecord = chunks
    .map((chunk) => chunk.split("="))
    .filter(([k]) => k == "user")[0];
  return JSON.parse(decodeURIComponent(userRecord[1]));
};

export function WebAppProvider({ children }: { children: React.ReactNode }) {
  const [webApp, setWebApp] = useState<WebApp | null>(null);
  const onLoad = useCallback(() => {
    console.log(
      "WebApp loaded",
      window.Telegram.WebApp.platform,
      settings.ENV,
      settings.DEBUG
    );
    if (
      window.Telegram.WebApp.platform === "unknown" &&
      settings.ENV === "development" &&
      settings.DEBUG
    ) {
      console.warn("Mock WebApp");
      setWebApp(mockWebApp());
      return;
    }
    //mockWebApp() if no in telegram
    //const userData = parseTGUserData(window.Telegram.WebApp.initData);
    // i18n.changeLanguage(userData.language_code);
    // theme.changeTheme(window.Telegram.WebApp.colorScheme)

    setWebApp(window.Telegram.WebApp);
    window.Telegram.WebApp.ready();
    window.Telegram.WebApp.expand();
  }, [setWebApp]);

  return (
    <>
      <WebAppContext.Provider value={webApp}>
        <Script src={TELEGRAM_SCRIPT_URL} onLoad={onLoad} />
        {children}
      </WebAppContext.Provider>
    </>
  );
}
