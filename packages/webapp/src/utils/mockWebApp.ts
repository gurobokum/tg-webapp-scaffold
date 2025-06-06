import { settings } from "@/conf";
import { WebApp } from "telegram";

// Mock the Telegram Web App to allow work with it in the browser
const mockWebApp = () => {
  if (typeof window === "undefined") {
    return null;
  }

  if (settings.ENV !== "development") {
    throw new Error("Mock WebApp is only available in development mode");
  }

  if (!settings.DEBUG) {
    throw new Error("Mock WebApp is only available in debug mode");
  }

  if (!process.env.NEXT_PUBLIC_MOCK_TELEGRAM) {
    return null;
  }

  if (window.Telegram?.WebApp?.initData) {
    return window.Telegram.WebApp;
  }

  const initData = process.env.NEXT_PUBLIC_MOCK_INIT_DATA;
  if (!initData) {
    throw new Error(
      "Please provide the NEXT_PUBLIC_MOCK_INIT_DATA environment variable"
    );
  }

  const webApp: WebApp = {
    ...(window.Telegram?.WebApp || {}),
    initData,
  };

  window.Telegram = {
    WebApp: webApp,
  };

  return webApp;
};

export default mockWebApp;
