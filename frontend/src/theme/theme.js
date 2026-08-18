import { alpha, createTheme } from "@mui/material/styles";

export const theme = createTheme({
  palette: {
    mode: "dark",
    background: { default: "#080d19", paper: alpha("#ffffff", 0.055) },
    primary: { main: "#8b5cf6" },
    secondary: { main: "#22d3ee" },
    success: { main: "#34d399" },
    warning: { main: "#fbbf24" },
    error: { main: "#fb7185" },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", sans-serif',
    h4: { fontWeight: 800 },
    h5: { fontWeight: 750 },
  },
  shape: { borderRadius: 18 },
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          background:
            "linear-gradient(135deg, rgba(255,255,255,.09), rgba(255,255,255,.035))",
          backdropFilter: "blur(18px)",
          border: "1px solid rgba(255,255,255,.10)",
          boxShadow: "0 20px 60px rgba(0,0,0,.24)",
        },
      },
    },
    MuiDialog: {
      styleOverrides: {
        paper: {
          background:
            "linear-gradient(135deg, rgba(17,24,39,0.97), rgba(31,41,55,0.97))",
          backdropFilter: "blur(20px)",
          border: "1px solid rgba(255,255,255,0.12)",
          borderRadius: 18,
          boxShadow: "0 25px 80px rgba(0,0,0,0.5)",
        },
      },
    },
    MuiButton: { defaultProps: { disableElevation: true } },
  },
});
