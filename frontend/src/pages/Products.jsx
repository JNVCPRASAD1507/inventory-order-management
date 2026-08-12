import { useEffect, useState } from "react";
import {
  Box, Button, Card, CardContent, Chip, Grid, TextField, Typography, Alert, CircularProgress, MenuItem
} from "@mui/material";
import api from "../api/client";
import { useAuth } from "../context/AuthContext";
import GlassCard from "../components/GlassCard";

export default function Products() {
  const { user } = useAuth();
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [q, setQ] = useState("");
  const [categoryId, setCategoryId] = useState("");
  const [loading, setLoading] = useState(true);
  const [msg, setMsg] = useState("");
  const [cart, setCart] = useState([]);
  const isStaff = user?.role === "admin" || user?.role === "staff";
  const isCustomer = user?.role === "customer";

  const load = async () => {
    setLoading(true);
    try {
      const params = {};
      if (q) params.q = q;
      if (categoryId) params.category_id = categoryId;
      const [p, c] = await Promise.all([
        api.get("/products", { params }),
        api.get("/categories"),
      ]);
      setProducts(p.data);
      setCategories(c.data);
    } catch (e) {
      setMsg(e.response?.data?.detail || "Failed to load products");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, [q, categoryId]);

  const addToCart = (p) => {
    setCart((prev) => {
      const ex = prev.find((i) => i.product_id === p.id);
      if (ex) return prev.map((i) => i.product_id === p.id ? { ...i, quantity: i.quantity + 1 } : i);
      return [...prev, { product_id: p.id, name: p.name, price: p.price, quantity: 1 }];
    });
  };

  const placeOrder = async () => {
    try {
      await api.post("/orders", { items: cart.map((c) => ({ product_id: c.product_id, quantity: c.quantity })) });
      setCart([]);
      setMsg("Order placed successfully");
      load();
    } catch (e) {
      setMsg(e.response?.data?.detail || "Order failed");
    }
  };

  return (
    <Box>
      <Typography variant="h4" fontWeight={800} mb={2}>Products</Typography>
      {msg && <Alert sx={{ mb: 2 }} onClose={() => setMsg("")}>{msg}</Alert>}
      <Box display="flex" gap={2} mb={3} flexWrap="wrap">
        <TextField size="small" label="Search" value={q} onChange={(e) => setQ(e.target.value)} />
        <TextField select size="small" label="Category" value={categoryId} onChange={(e) => setCategoryId(e.target.value)} sx={{ minWidth: 160 }}>
          <MenuItem value="">All</MenuItem>
          {categories.map((c) => <MenuItem key={c.id} value={c.id}>{c.name}</MenuItem>)}
        </TextField>
      </Box>
      {isCustomer && cart.length > 0 && (
        <GlassCard sx={{ mb: 3, p: 2 }}>
          <Typography fontWeight={700}>Cart ({cart.reduce((s, i) => s + i.quantity, 0)})</Typography>
          {cart.map((i) => (
            <Typography key={i.product_id} variant="body2">{i.name} × {i.quantity} = ₹{(Number(i.price) * i.quantity).toFixed(2)}</Typography>
          ))}
          <Button variant="contained" sx={{ mt: 1 }} onClick={placeOrder}>Place Order</Button>
        </GlassCard>
      )}
      {loading ? <CircularProgress /> : (
        <Grid container spacing={2}>
          {products.map((p) => (
            <Grid item xs={12} sm={6} md={4} lg={3} key={p.id}>
              <Card sx={{ height: "100%", background: "rgba(255,255,255,0.04)", border: "1px solid rgba(255,255,255,0.08)" }}>
                <CardContent>
                  <Typography fontWeight={700} noWrap>{p.name}</Typography>
                  <Typography variant="body2" color="text.secondary" noWrap>{p.sku}</Typography>
                  <Typography variant="h6" color="secondary" mt={1}>₹{Number(p.price).toLocaleString()}</Typography>
                  <Chip size="small" label={`Stock: ${p.stock_quantity ?? p.current_stock ?? 0}`} sx={{ mt: 1 }} />
                  {isCustomer && (
                    <Button fullWidth size="small" variant="outlined" sx={{ mt: 1.5 }} onClick={() => addToCart(p)}>Add to cart</Button>
                  )}
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}
    </Box>
  );
}
