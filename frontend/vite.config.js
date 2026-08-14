import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: { port: 5173, host: "0.0.0.0" }
  // server: { port: 5173, host: "0.0.0.0" || "10.138.134.207" || "localhost" || "172.26.0.1"},

});
