import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: { port: 5173,
      host: "localhost",
     // host: true // Vite listens on all network interfaces like Network: http://192.168.137.1:5173/ , Network: http://10.100.110.207:5173/
       }
});
