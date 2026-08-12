import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Alert, Box, Button, Card, CardContent, TextField, Typography } from "@mui/material";
import { useAuth } from "../context/AuthContext";

export default function Login() {
  const [email, setEmail] = useState("admin@example.com");
  const [password, setPassword] = useState("admin123");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const onSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await login(email, password);
      navigate("/");
    } catch (err) {
      setError(err.response?.data?.detail || "Login failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box minHeight="100vh" display="flex" alignItems="center" justifyContent="center" sx={{
      background: "radial-gradient(circle at 20% 20%, rgba(139,92,246,.25), transparent 40%), radial-gradient(circle at 80% 0%, rgba(34,211,238,.2), transparent 35%), #080d19"
    }}>
      <Card sx={{ width: 420, background: "rgba(255,255,255,0.06)", backdropFilter: "blur(18px)", border: "1px solid rgba(255,255,255,0.1)" }}>
        <CardContent sx={{ p: 3 }}>
          <Typography variant="h4" fontWeight={900} textAlign="center" gutterBottom>
            Inventory<span style={{ color: "#22d3ee" }}>OS</span>
          </Typography>
          <Typography variant="body2" color="text.secondary" textAlign="center" mb={2}>Sign in to continue</Typography>
          {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
          <Box component="form" onSubmit={onSubmit}>
            <TextField fullWidth label="Email" margin="normal" value={email} onChange={(e) => setEmail(e.target.value)} required />
            <TextField fullWidth type="password" label="Password" margin="normal" value={password} onChange={(e) => setPassword(e.target.value)} required />
            <Button fullWidth type="submit" variant="contained" size="large" sx={{ mt: 2 }} disabled={loading}>
              {loading ? "Signing in…" : "Sign In"}
            </Button>
          </Box>
          <Box mt={2} p={1.5} borderRadius={2} bgcolor="rgba(0,0,0,0.25)">
            <Typography variant="caption" display="block">Demo: admin@example.com / admin123</Typography>
            <Typography variant="caption" display="block">staff@example.com / staff123</Typography>
            <Typography variant="caption" display="block">customer@example.com / customer123</Typography>
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
}
