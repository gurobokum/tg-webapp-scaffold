import { defineConfig } from "@hey-api/openapi-ts";
import { defaultPlugins } from "@hey-api/openapi-ts";

export default defineConfig({
  input: "./openapi.json",
  output: {
    path: "src/client/",
    format: "prettier",
    lint: "eslint",
  },
  plugins: [
    { name: "@hey-api/client-fetch" },
    ...defaultPlugins,
    {
      name: "@hey-api/sdk",
      asClass: false,
      operationId: true,
    },
  ],
});
