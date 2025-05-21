"use client";

import { useMemo } from "react";
import { FiZap, FiPackage, FiStar, FiAward } from "react-icons/fi";
import { motion } from "framer-motion";
import cn from "clsx";

import { CreditsPackage } from "@tg-webapp/sdk";
import { Language } from "@/i18n/conf";
import { useTranslation } from "@/i18n/client";

type PackageInfo = {
  name: string;
  popular: boolean;
  icon: React.ReactNode;
};

const packages: Record<string, PackageInfo> = {
  starter_1705: {
    name: "starter",
    popular: false,
    icon: <FiPackage />,
  },
  business_1705: {
    name: "business",
    popular: true,
    icon: <FiStar />,
  },
  agency_1705: {
    name: "agency",
    popular: false,
    icon: <FiAward />,
  },
};

export function PackageBlock({
  pkg,
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  index,
  lang,
  onPackageSelect,
  isSelected,
}: {
  pkg: CreditsPackage;
  index: number;
  lang: Language;
  onPackageSelect: (pkg: CreditsPackage) => void;
  isSelected: boolean;
}) {
  const { t } = useTranslation(lang, "app", {
    keyPrefix: "payment._components.PackageBlock",
  });
  const pkgInfo = useMemo(() => {
    return packages[pkg.package_name];
  }, [pkg]);

  if (!pkgInfo) {
    return null;
  }

  return (
    <motion.div
      variants={{
        hidden: { opacity: 0, y: 20 },
        show: { opacity: 1, y: 0 },
      }}
      whileHover={{ scale: 1.02 }}
      className={cn(
        "card cursor-pointer transition-all overflow-visible",
        isSelected
          ? "bg-primary/10 bg-opacity-10 border-2 border-primary py-2"
          : "bg-base-200 hover:bg-base-300 border-2 border-transparent"
      )}
      onClick={() => onPackageSelect(pkg)}
    >
      {pkgInfo.popular && (
        <div className="absolute -top-3 -right-2 badge badge-primary badge-sm py-1">
          {t("popular")}
        </div>
      )}

      <div className="card-body p-4">
        <div className="flex items-center">
          <div
            className={cn(
              "text-2xl mr-3",
              isSelected ? "text-primary" : "text-base-content/70"
            )}
          >
            {pkgInfo.icon}
          </div>
          <div>
            <h3 className="font-semibold">{t(pkgInfo.name)}</h3>
            <div className="flex items-center text-sm">
              <FiZap className="text-secondary-content mr-1" />
              <span>
                {pkg.credits_amount.toLocaleString()}{" "}
                {t("credits", { count: pkg.credits_amount })}
              </span>
            </div>
          </div>
          <div className="ml-auto">
            <div className="text-lg font-semibold">☆ {pkg.stars_amount}</div>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
