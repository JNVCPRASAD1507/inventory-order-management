import { useEffect, useState } from "react";
import { Alert, Box, Grid, Typography } from "@mui/material";
import PeopleRoundedIcon from "@mui/icons-material/PeopleRounded";
import InventoryRoundedIcon from "@mui/icons-material/InventoryRounded";
import ShoppingCartRoundedIcon from "@mui/icons-material/ShoppingCartRounded";
import WarningRoundedIcon from "@mui/icons-material/WarningRounded";
import PaymentsRoundedIcon from "@mui/icons-material/PaymentsRounded";
import StatCard from "../components/StatCard";
import ChartCard from "../components/ChartCard";
import GlassCard from "../components/GlassCard";
import api from "../api/client";
import { useAuth } from "../context/AuthContext";

export default function Dashboard() {
  const { user } = useAuth();
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    const role =
      user?.role === "admin"
        ? "admin"
        : user?.role === "staff"
          ? "staff"
          : "customer";
    api
      .get(`/dashboard/${role}`)
      .then((r) => setData(r.data))
      .catch((e) => setError(e.response?.data?.detail || "Dashboard failed"));
  }, [user]);

  if (error) return <Alert severity="error">{error}</Alert>;
  if (!data) return <Typography>Loading dashboard...</Typography>;

  if (user?.role === "customer") {
    return (
      <Box>
        <Typography variant="h4" mb={3}>
          Customer Dashboard
        </Typography>
        <Grid container spacing={2}>
          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <StatCard
              label="Total Orders"
              value={data.total_orders}
              icon={ShoppingCartRoundedIcon}
            />
          </Grid>
          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <StatCard
              label="Pending"
              value={data.pending_orders}
              icon={WarningRoundedIcon}
            />
          </Grid>
          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <StatCard
              label="Completed"
              value={data.completed_orders}
              icon={InventoryRoundedIcon}
            />
          </Grid>
          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <StatCard
              label="Amount Spent"
              value={`₹${data.total_amount_spent.toFixed(2)}`}
              icon={PaymentsRoundedIcon}
            />
          </Grid>
        </Grid>
      </Box>
    );
  }

  const m = data.metrics || data;
  return (
    <Box>
      <Typography variant="h4" mb={3}>
        Good morning, {user?.full_name?.split(" ")[0]}
      </Typography>
      <Grid container spacing={2} mb={2}>
        <Grid size={{ xs: 12, sm: 6, lg: 3 }}>
          <StatCard
            label="Customers"
            value={m.total_customers || "—"}
            icon={PeopleRoundedIcon}
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, lg: 3 }}>
          <StatCard
            label="Products"
            value={m.total_products}
            icon={InventoryRoundedIcon}
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, lg: 3 }}>
          <StatCard
            label="Orders"
            value={m.total_orders}
            icon={ShoppingCartRoundedIcon}
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, lg: 3 }}>
          <StatCard
            label="Low Stock"
            value={m.low_stock_products}
            icon={WarningRoundedIcon}
          />
        </Grid>
      </Grid>
      <Grid container spacing={2}>
        <Grid size={{ xs: 12, lg: 8 }}>
          <ChartCard
            datasets={{
              daily: data.daily,
              weekly: data.weekly,
              monthly: data.monthly,
            }}
          />
        </Grid>
        <Grid size={{ xs: 12, lg: 4 }}>
          <GlassCard sx={{ height: 390 }}>
            <Typography variant="h6" fontWeight={800}>
              Revenue
            </Typography>
            <Typography variant="h3" mt={2}>
              ₹{Number(m.total_revenue || 0).toLocaleString()}
            </Typography>
            <Typography color="text.secondary" mt={1}>
              Revenue from paid orders
            </Typography>
          </GlassCard>
        </Grid>
      </Grid>
    </Box>
  );
}
