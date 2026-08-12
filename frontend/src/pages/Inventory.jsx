import { useEffect, useState } from "react";
import { Box, Button, Chip, Table, TableBody, TableCell, TableHead, TableRow, Typography, Alert, Paper, TextField, Dialog, DialogTitle, DialogContent, DialogActions } from "@mui/material";
import api from "../api/client";

export default function Inventory() {
  const [rows, setRows] = useState([]);
  const [msg, setMsg] = useState("");
  const [dlg, setDlg] = useState({ open: false, productId: null, qty: 10, type: "add" });

  const load = async () => {
    try {
      const res = await api.get("/inventory");
      setRows(res.data);
    } catch (e) {
      setMsg(e.response?.data?.detail || "Failed");
    }
  };
  useEffect(() => { load(); }, []);

  const submit = async () => {
    try {
      const path = dlg.type === "add" ? "add-stock" : "remove-stock";
      await api.post(`/inventory/${dlg.productId}/${path}`, { quantity: dlg.qty });
      setDlg({ ...dlg, open: false });
      setMsg("Stock updated");
      load();
    } catch (e) {
      setMsg(e.response?.data?.detail || "Failed");
    }
  };

  return (
    <Box>
      <Typography variant="h4" fontWeight={800} mb={2}>Inventory</Typography>
      {msg && <Alert sx={{ mb: 2 }} onClose={() => setMsg("")}>{msg}</Alert>}
      <Paper sx={{ background: "rgba(255,255,255,0.04)" }}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Product</TableCell>
              <TableCell>Stock</TableCell>
              <TableCell>Min</TableCell>
              <TableCell>Max</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {rows.map((r) => (
              <TableRow key={r.id || r.product_id}>
                <TableCell>{r.product_name || r.product_id}</TableCell>
                <TableCell>{r.current_stock}</TableCell>
                <TableCell>{r.minimum_stock_level ?? r.min_stock_level}</TableCell>
                <TableCell>{r.maximum_stock_level ?? r.max_stock_level}</TableCell>
                <TableCell>
                  <Chip size="small" label={(r.current_stock <= (r.minimum_stock_level ?? 10)) ? "Low" : "OK"} color={(r.current_stock <= (r.minimum_stock_level ?? 10)) ? "error" : "success"} />
                </TableCell>
                <TableCell>
                  <Button size="small" onClick={() => setDlg({ open: true, productId: r.product_id, qty: 10, type: "add" })}>+ Stock</Button>
                  <Button size="small" color="warning" onClick={() => setDlg({ open: true, productId: r.product_id, qty: 1, type: "remove" })}>- Stock</Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Paper>
      <Dialog open={dlg.open} onClose={() => setDlg({ ...dlg, open: false })}>
        <DialogTitle>{dlg.type === "add" ? "Add Stock" : "Remove Stock"}</DialogTitle>
        <DialogContent>
          <TextField type="number" fullWidth margin="dense" label="Quantity" value={dlg.qty} onChange={(e) => setDlg({ ...dlg, qty: Number(e.target.value) })} />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDlg({ ...dlg, open: false })}>Cancel</Button>
          <Button variant="contained" onClick={submit}>Confirm</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
