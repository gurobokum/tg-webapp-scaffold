export default {
  "backend/**": () => ["pnpm backend:lint", "pnpm backend:mypy"],
  "webapp/**": () => [
    "pnpm webapp:lint",
    "pnpm webapp:format:check",
    "pnpm webapp:ts",
  ],
};
