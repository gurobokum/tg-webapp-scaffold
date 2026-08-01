import { NextResponse } from "next/server";
import acceptLanguage from "accept-language";
import { NextRequest } from "next/server";
import { cookieName, fallbackLang } from "@/i18n/conf";

const languages = ["ru", "en"];
acceptLanguage.languages(languages);

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

  if (!lang || !languages.includes(lang)) {
    lang = fallbackLang;
  }

  const firstSegment = request.nextUrl.pathname.split("/")[1];

  if (
    !languages.includes(firstSegment) &&
    !request.nextUrl.pathname.startsWith("/_next")
  ) {
    return NextResponse.redirect(
      new URL(`/${lang}${request.nextUrl.pathname}`, request.url)
    );
  }

  const referer = request.headers.get("referer");
  if (referer) {
    const refererUrl = new URL(referer);
    const langInReferer = languages.find((lang) =>
      refererUrl.pathname.startsWith(`/${lang}`)
    );
    const response = NextResponse.next();
    if (langInReferer) {
      response.cookies.set(cookieName, langInReferer);
    }
    return response;
  }

  return NextResponse.next();
}
