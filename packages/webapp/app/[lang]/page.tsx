import PageTransition from "@/components/PageTransition";
import UserInfo from "@/components/UserInfo";
import { getTranslation } from "@/i18n";
import { Language } from "@/i18n/conf";

export default async function Home({
  params,
}: {
  params: Promise<{ lang: Language }>;
}) {
  const { lang } = await params;
  const { t } = await getTranslation(lang, "app", { keyPrefix: "root" });

  return (
    <PageTransition>
      <div className="container mx-auto max-w-md p-4">
        <UserInfo />
        <h1 className="text-2xl font-bold mb-6">{t("title")}</h1>
      </div>
    </PageTransition>
  );
}
