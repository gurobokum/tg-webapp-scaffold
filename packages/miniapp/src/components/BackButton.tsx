"use client";

import { useCallback, useContext, useEffect } from "react";
import { useRouter } from "next/navigation";

import { WebAppContext } from "@/providers/WebAppProvider";

export function BackButton({ href }: { href?: string }) {
  const webApp = useContext(WebAppContext);
  const router = useRouter();

  const onBackButtonClick = useCallback(() => {
    if (href) {
      router.push(href);
    } else {
      router.back();
    }
  }, [router, href]);

  useEffect(() => {
    if (!webApp) return;

    webApp.BackButton.onClick(onBackButtonClick);
    webApp.BackButton.show();
    return () => {
      webApp.BackButton.offClick(onBackButtonClick);
      webApp.BackButton.hide();
    };
  }, [onBackButtonClick, webApp]);

  if (webApp?.platform == "unknown") {
    return (
      <button
        onClick={onBackButtonClick}
        className="btn btn-gost absolute left-2 top-2"
      >
        ‹ Back
      </button>
    );
  }

  return null;
}
