import { useEffect, useState } from "react";
import { Box, Button, List, ListItem, ListItemText, Typography, Paper, Chip } from "@mui/material";
import api from "../api/client";

export default function Notifications() {
  const [items, setItems] = useState([]);

  const load = async () => {
    try {
      const res = await api.get("/notifications");
      setItems(res.data);
    } catch {}
  };
  useEffect(() => { load(); }, []);

  const mark = async (id) => {
    try {
      await api.put(`/notifications/${id}/read`);
      load();
    } catch {}
  };

  return (
    <Box>
      <Typography variant="h4" fontWeight={800} mb={2}>Notifications</Typography>
      <Paper sx={{ background: "rgba(255,255,255,0.04)" }}>
        <List>
          {items.length === 0 && <ListItem><ListItemText primary="No notifications" /></ListItem>}
          {items.map((n) => (
            <ListItem key={n.id} secondaryAction={!n.is_read && <Button size="small" onClick={() => mark(n.id)}>Mark read</Button>}
              sx={{ bgcolor: n.is_read ? "transparent" : "rgba(139,92,246,0.08)" }}>
              <ListItemText
                primary={<Box display="flex" gap={1} alignItems="center">{n.title} {!n.is_read && <Chip size="small" label="New" color="primary" />}</Box>}
                secondary={<>{n.message}<br /><Typography variant="caption">{n.created_at && new Date(n.created_at).toLocaleString()}</Typography></>}
              />
            </ListItem>
          ))}
        </List>
      </Paper>
    </Box>
  );
}
