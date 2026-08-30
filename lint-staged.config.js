export default {
  "packages/backend/**": () => ["pnpm backend:lint", "pnpm backend:mypy"],
  "packages/webapp/**": () => [
    "pnpm webapp:lint",
    "pnpm webapp:format:check",
    "pnpm webapp:ts",
  ],
};
