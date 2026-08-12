import { useEffect, useState } from "react";
import {
  Box, Button, Chip, Table, TableBody, TableCell, TableHead, TableRow, Typography, Alert, CircularProgress, Paper
} from "@mui/material";
import api from "../api/client";
import { useAuth } from "../context/AuthContext";

const colors = { pending: "warning", confirmed: "info", shipped: "primary", delivered: "success", cancelled: "error" };

export default function Orders() {
  const { user } = useAuth();
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [msg, setMsg] = useState("");
  const isStaff = user?.role === "admin" || user?.role === "staff";

  const load = async () => {
    setLoading(true);
    try {
      const res = await api.get("/orders");
      setOrders(res.data);
    } catch (e) {
      setMsg(e.response?.data?.detail || "Failed");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const act = async (action, id) => {
    try {
      if (action === "pay") await api.post("/payments", { order_id: id, payment_method: "upi" });
      else await api.put(`/orders/${id}/${action}`);
      setMsg(`Order ${action} OK`);
      load();
    } catch (e) {
      setMsg(e.response?.data?.detail || "Action failed");
    }
  };

  return (
    <Box>
      <Typography variant="h4" fontWeight={800} mb={2}>Orders</Typography>
      {msg && <Alert sx={{ mb: 2 }} onClose={() => setMsg("")}>{msg}</Alert>}
      {loading ? <CircularProgress /> : (
        <Paper sx={{ background: "rgba(255,255,255,0.04)", overflow: "auto" }}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>ID</TableCell>
                <TableCell>Date</TableCell>
                <TableCell>Total</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {orders.map((o) => (
                <TableRow key={o.id}>
                  <TableCell>#{o.id}</TableCell>
                  <TableCell>{o.created_at ? new Date(o.created_at).toLocaleString() : o.order_date ? new Date(o.order_date).toLocaleString() : "-"}</TableCell>
                  <TableCell>₹{Number(o.total_amount).toLocaleString()}</TableCell>
                  <TableCell><Chip size="small" label={o.status} color={colors[o.status] || "default"} /></TableCell>
                  <TableCell>
                    {isStaff && o.status === "pending" && <Button size="small" onClick={() => act("confirm", o.id)}>Confirm</Button>}
                    {isStaff && o.status === "confirmed" && <Button size="small" onClick={() => act("ship", o.id)}>Ship</Button>}
                    {isStaff && o.status === "shipped" && <Button size="small" onClick={() => act("deliver", o.id)}>Deliver</Button>}
                    {(o.status === "pending" || o.status === "confirmed") && <Button size="small" color="error" onClick={() => act("cancel", o.id)}>Cancel</Button>}
                    {user?.role === "customer" && o.status === "pending" && <Button size="small" color="secondary" onClick={() => act("pay", o.id)}>Pay</Button>}
                  </TableCell>
                </TableRow>
              ))}
              {orders.length === 0 && <TableRow><TableCell colSpan={5}>No orders</TableCell></TableRow>}
            </TableBody>
          </Table>
        </Paper>
      )}
    </Box>
  );
}
