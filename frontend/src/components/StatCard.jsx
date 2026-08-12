import { Box, Typography } from "@mui/material";
import GlassCard from "./GlassCard";

export default function StatCard({ label, value, icon: Icon }) {
  return (
    <GlassCard>
      <Box display="flex" justifyContent="space-between" alignItems="center">
        <Box>
          <Typography variant="body2" color="text.secondary">{label}</Typography>
          <Typography variant="h4" mt={0.7}>{value}</Typography>
        </Box>
        {Icon && <Box sx={{ p: 1.2, borderRadius: 3, background: "linear-gradient(135deg,#8b5cf6,#22d3ee)" }}><Icon /></Box>}
      </Box>
    </GlassCard>
  );
}
