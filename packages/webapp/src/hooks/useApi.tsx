"use client";

import { settings } from "@/conf";
import { WebAppContext } from "@/providers/WebAppProvider";
import { client } from "@tg-webapp/sdk";
import { useContext, useMemo } from "react";

export function useApi() {
  const webApp = useContext(WebAppContext);

  return useMemo(() => {
    if (!webApp?.initData) {
      return null;
    }

    client.setConfig({
      baseUrl: settings.API_URL,
      headers: {
        "X-Telegram-Auth": webApp.initData,
      },
    });
    return client;
  }, [webApp]);
}
