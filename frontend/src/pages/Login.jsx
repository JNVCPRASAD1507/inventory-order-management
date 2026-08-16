import { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  TextField,
  Typography,
  IconButton,
  InputAdornment,
} from "@mui/material";

import Visibility from "@mui/icons-material/Visibility";
import VisibilityOff from "@mui/icons-material/VisibilityOff";
import { useAuth } from "../context/AuthContext";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
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
    <Box
      minHeight="100vh"
      display="flex"
      alignItems="center"
      justifyContent="center"
      sx={{
        background:
          "radial-gradient(circle at 20% 20%, rgba(139,92,246,.25), transparent 40%), radial-gradient(circle at 80% 0%, rgba(34,211,238,.2), transparent 35%), #080d19",
      }}
    >
      <Card
        sx={{
          width: 420,
          background: "rgba(255,255,255,0.06)",
          backdropFilter: "blur(18px)",
          border: "1px solid rgba(255,255,255,0.1)",
        }}
      >
        <CardContent sx={{ p: 3 }}>
          {/* Logo / Title */}
          <Typography
            variant="h4"
            fontWeight={900}
            textAlign="center"
            gutterBottom
          >
            Inventory
            <span style={{ color: "#22d3ee" }}>OS</span>
          </Typography>

          <Typography
            variant="body2"
            color="text.secondary"
            textAlign="center"
            mb={2}
          >
            Sign in to your account
          </Typography>

          {/* Error */}
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          {/* Login Form */}
          <Box component="form" onSubmit={onSubmit}>
            <TextField
              fullWidth
              label="Email"
              margin="normal"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />

            {/* <TextField
              fullWidth
              type="password"
              label="Password"
              margin="normal"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            /> */}
            <TextField
              fullWidth
              type={showPassword ? "text" : "password"}
              label="Password"
              margin="normal"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              slotProps={{
                input: {
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton
                        onClick={() => setShowPassword((prev) => !prev)}
                        edge="end"
                        aria-label={
                          showPassword ? "Hide password" : "Show password"
                        }
                      >
                        {showPassword ? <VisibilityOff /> : <Visibility />}
                      </IconButton>
                    </InputAdornment>
                  ),
                },
              }}
            />

            <Button
              fullWidth
              type="submit"
              variant="contained"
              size="large"
              sx={{ mt: 2 }}
              disabled={loading}
            >
              {loading ? "Signing in…" : "Sign In"}
            </Button>
          </Box>

          {/* Forgot Password */}
          <Box
            sx={{
              display: "flex",
              justifyContent: "center",
              mt: 2,
            }}
          >
            <Button
              variant="text"
              onClick={() => navigate("/forgot-password")}
              sx={{
                textTransform: "none",
                minWidth: "auto",
                p: 0,
              }}
            >
              Forgot Password?
            </Button>
          </Box>

          {/* Sign Up */}
          <Box
            sx={{
              mt: 1,
              display: "flex",
              justifyContent: "center",
              alignItems: "center",
              gap: 0.5,
            }}
          >
            <Typography variant="body2">Don't have an account?</Typography>

            <Button
              variant="text"
              onClick={() => navigate("/signup")}
              sx={{
                textTransform: "none",
                minWidth: "auto",
                p: 0,
              }}
            >
              Sign Up
            </Button>
          </Box>

          {/* Demo credentials */}
          {/*
          <Box mt={2} p={1.5} borderRadius={2} bgcolor="rgba(0,0,0,0.25)">
            <Typography variant="caption" display="block">
              Demo: admin@example.com / admin123
            </Typography>
            <Typography variant="caption" display="block">
              Demo: staff@example.com / staff123
            </Typography>
            <Typography variant="caption" display="block">
              Demo: customer@example.com / customer123
            </Typography>
          </Box>
          */}
        </CardContent>
      </Card>
    </Box>
  );
}
