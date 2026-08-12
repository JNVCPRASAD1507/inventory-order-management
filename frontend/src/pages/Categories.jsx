import { useEffect, useState } from "react";
import { Box, Button, TextField, Table, TableBody, TableCell, TableHead, TableRow, Typography, Alert, Paper, Dialog, DialogTitle, DialogContent, DialogActions } from "@mui/material";
import api from "../api/client";
import { useAuth } from "../context/AuthContext";

export default function Categories() {
  const { user } = useAuth();
  const [rows, setRows] = useState([]);
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({ name: "", description: "" });
  const [msg, setMsg] = useState("");
  const isAdmin = user?.role === "admin";

  const load = async () => {
    try {
      const res = await api.get("/categories");
      setRows(res.data);
    } catch (e) {
      setMsg(e.response?.data?.detail || "Failed");
    }
  };
  useEffect(() => { load(); }, []);

  const create = async () => {
    try {
      await api.post("/categories", form);
      setOpen(false);
      setForm({ name: "", description: "" });
      setMsg("Created");
      load();
    } catch (e) {
      setMsg(e.response?.data?.detail || "Failed");
    }
  };

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" mb={2}>
        <Typography variant="h4" fontWeight={800}>Categories</Typography>
        {isAdmin && <Button variant="contained" onClick={() => setOpen(true)}>Add</Button>}
      </Box>
      {msg && <Alert sx={{ mb: 2 }} onClose={() => setMsg("")}>{msg}</Alert>}
      <Paper sx={{ background: "rgba(255,255,255,0.04)" }}>
        <Table>
          <TableHead><TableRow><TableCell>ID</TableCell><TableCell>Name</TableCell><TableCell>Description</TableCell><TableCell>Status</TableCell></TableRow></TableHead>
          <TableBody>
            {rows.map((r) => (
              <TableRow key={r.id}>
                <TableCell>{r.id}</TableCell>
                <TableCell>{r.name}</TableCell>
                <TableCell>{r.description}</TableCell>
                <TableCell>{r.status || (r.is_active ? "active" : "inactive")}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Paper>
      <Dialog open={open} onClose={() => setOpen(false)}>
        <DialogTitle>New Category</DialogTitle>
        <DialogContent>
          <TextField fullWidth margin="dense" label="Name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
          <TextField fullWidth margin="dense" label="Description" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={create}>Create</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
