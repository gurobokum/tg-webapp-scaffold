import { z } from "zod";

// !! Pass only NEXT_PUBLIC_ variables to the client side !!;

const SettingsSchema = z.object({
  API_URL: z.string().url(),
  ENV: z.enum(["development", "production", "test"]),
  DEBUG: z.boolean(),
});

export const settings = SettingsSchema.parse({
  API_URL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
  ENV: process.env.NODE_ENV,
  DEBUG:
    process.env.NODE_ENV === "development" &&
    process.env.NEXT_PUBLIC_DEBUG === "true",
});
