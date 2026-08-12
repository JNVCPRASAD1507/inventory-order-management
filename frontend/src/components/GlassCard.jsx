import { Card } from "@mui/material";

export default function GlassCard({ children, sx = {}, ...props }) {
  return (
    <Card
      {...props}
      sx={{
        p: 2.5,
        background: "linear-gradient(135deg, rgba(255,255,255,.10), rgba(139,92,246,.055) 45%, rgba(34,211,238,.045))",
        backdropFilter: "blur(20px)",
        border: "1px solid rgba(255,255,255,.11)",
        ...sx
      }}
    >
      {children}
    </Card>
  );
}
