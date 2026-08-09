import { NextResponse } from "next/server";
import acceptLanguage from "accept-language";
import { NextRequest } from "next/server";
import {
  cookieName,
  fallbackLang,
  isSupportedLanguage,
  languages,
} from "@/i18n/conf";

acceptLanguage.languages([...languages]);

export const config = {
  // matcher: '/:lang*'
  matcher: [
    "/((?!api|_next/static|_next/image|assets|favicon.ico|sw.js|site.webmanifest).*)",
  ],
};

// https://www.locize.com/blog/next-app-dir-i18n
export function proxy(request: NextRequest) {
  let lang;

  if (request.cookies.has(cookieName)) {
    lang = request.cookies.get(cookieName)?.value;
  }

  if (!lang) {
    lang = acceptLanguage.get(request.headers.get("Accept-Language"));
  }

  if (!lang || !isSupportedLanguage(lang)) {
    lang = fallbackLang;
  }

  const firstSegment = request.nextUrl.pathname.split("/")[1];

  if (
    !isSupportedLanguage(firstSegment) &&
    !request.nextUrl.pathname.startsWith("/_next")
  ) {
    return NextResponse.redirect(
      new URL(`/${lang}${request.nextUrl.pathname}`, request.url)
    );
  }

  const referer = request.headers.get("referer");
  if (referer) {
    const refererUrl = new URL(referer);
    const refererFirstSegment = refererUrl.pathname.split("/")[1];
    const langInReferer = isSupportedLanguage(refererFirstSegment)
      ? refererFirstSegment
      : undefined;
    const response = NextResponse.next();
    if (langInReferer) {
      response.cookies.set(cookieName, langInReferer);
    }
    return response;
  }

  return NextResponse.next();
}
