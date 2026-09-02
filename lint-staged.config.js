export default {
  "packages/backend/**": () => ["pnpm backend:lint", "pnpm backend:mypy"],
  "packages/miniapp/**": () => [
    "pnpm miniapp:lint",
    "pnpm miniapp:format:check",
    "pnpm miniapp:ts",
  ],
};
