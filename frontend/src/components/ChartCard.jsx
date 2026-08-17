import { useState } from "react";
import { Box, FormControl, MenuItem, Select, Typography } from "@mui/material";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

import GlassCard from "./GlassCard";

export default function ChartCard({ datasets }) {
  const [range, setRange] = useState("daily");

  const data = datasets?.[range] || [];

  return (
    <GlassCard sx={{ height: 390 }}>
      <Box
        display="flex"
        justifyContent="space-between"
        alignItems="center"
        mb={2}
      >
        <Box>
          <Typography variant="h6" fontWeight={750}>
            Order & Revenue Analytics
          </Typography>

          <Typography variant="body2" color="text.secondary">
            Orders and revenue over time
          </Typography>
        </Box>

        <FormControl size="small" sx={{ minWidth: 120 }}>
          <Select value={range} onChange={(e) => setRange(e.target.value)}>
            <MenuItem value="daily">Daily</MenuItem>

            <MenuItem value="weekly">Weekly</MenuItem>

            <MenuItem value="monthly">Monthly</MenuItem>
          </Select>
        </FormControl>
      </Box>

      <ResponsiveContainer width="100%" height="82%">
        <LineChart
          data={data}
          margin={{
            top: 10,
            right: 20,
            left: 0,
            bottom: 10,
          }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,.08)" />

          <XAxis dataKey="date" stroke="#94a3b8" tick={{ fontSize: 12 }} />

          <YAxis stroke="#94a3b8" tick={{ fontSize: 12 }} />

          <Tooltip
            contentStyle={{
              background: "#111827",
              border: "1px solid rgba(255,255,255,.15)",
              borderRadius: 12,
            }}
          />

          <Line
            type="monotone"
            dataKey="orders"
            stroke="#22d3ee"
            strokeWidth={3}
            dot={{ r: 3 }}
            activeDot={{ r: 6 }}
          />

          <Line
            type="monotone"
            dataKey="revenue"
            stroke="#8b5cf6"
            strokeWidth={3}
            dot={{ r: 3 }}
            activeDot={{ r: 6 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </GlassCard>
  );
}

// import { useState } from "react";
// import { Box, FormControl, MenuItem, Select, Typography } from "@mui/material";
// import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
// import GlassCard from "./GlassCard";

// export default function ChartCard({ datasets }) {
//   const [range, setRange] = useState("daily");
//   const data = datasets?.[range] || [];

//   return (
//     <GlassCard sx={{ height: 390 }}>
//       <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
//         <Box>
//           <Typography variant="h6" fontWeight={750}>Order & Revenue Analytics</Typography>
//           <Typography variant="body2" color="text.secondary">Change the menu to switch aggregation</Typography>
//         </Box>
//         <FormControl size="small" sx={{ minWidth: 120 }}>
//           <Select value={range} onChange={(e) => setRange(e.target.value)}>
//             <MenuItem value="daily">Daily</MenuItem>
//             <MenuItem value="weekly">Weekly</MenuItem>
//             <MenuItem value="monthly">Monthly</MenuItem>
//           </Select>
//         </FormControl>
//       </Box>
//       <ResponsiveContainer width="100%" height="82%">
//         <LineChart data={data}>
//           <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,.08)" />
//           <XAxis dataKey="date" stroke="#94a3b8" />
//           <YAxis stroke="#94a3b8" />
//           <Tooltip contentStyle={{ background: "#111827", border: "1px solid rgba(255,255,255,.15)", borderRadius: 12 }} />
//           <Line type="monotone" dataKey="orders" stroke="#22d3ee" strokeWidth={3} dot={false} />
//           <Line type="monotone" dataKey="revenue" stroke="#8b5cf6" strokeWidth={3} dot={false} />
//         </LineChart>
//       </ResponsiveContainer>
//     </GlassCard>
//   );
// }
