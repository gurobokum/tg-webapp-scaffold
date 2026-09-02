"use client";

import { useTranslation } from "@/i18n/client";
import { Language } from "@/i18n/conf";
import { AnimatePresence, motion } from "framer-motion";
import { useParams, useRouter } from "next/navigation";
import { useState } from "react";
import { FiZap } from "react-icons/fi";

export default function CreditsBlock({ credits }: { credits: number }) {
  const { lang } = useParams<{ lang: Language }>();
  const [showCreditPulse] = useState(false);
  const { t } = useTranslation(lang, "components", {
    keyPrefix: "CreditsBlock",
  });
  const router = useRouter();

  return (
    <motion.div
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      className="relative flex items-center bg-base-200 px-3 py-2 rounded-full cursor-pointer hover:bg-base-300 transition-colors overflow-hidden"
      onClick={() => router.push("/payment")}
      animate={
        showCreditPulse
          ? {
              boxShadow: [
                "0 0 0 rgba(0,0,0,0)",
                "0 0 0 rgba(0,0,0,0)",
                "0 0 8px rgba(255, 215, 0, 0.4)",
                "0 0 0 rgba(0,0,0,0)",
              ],
            }
          : {}
      }
      transition={{ duration: 1.5 }}
    >
      {showCreditPulse && (
        <motion.div
          className="absolute inset-0 bg-gradient-to-r from-transparent via-amber-200 to-transparent opacity-20"
          initial={{ x: "-100%" }}
          animate={{ x: "100%" }}
          transition={{ duration: 1, ease: "easeInOut" }}
        />
      )}

      <AnimatePresence>
        <motion.div
          animate={showCreditPulse ? "pulse" : "idle"}
          className="mr-2 text-secondary-content relative z-10"
        >
          <FiZap />
        </motion.div>
      </AnimatePresence>
      <span className="font-semibold text-sm relative z-10">
        {credits.toLocaleString()} {t("credits")}
      </span>
    </motion.div>
  );
}
