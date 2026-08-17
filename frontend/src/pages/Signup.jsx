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
  MenuItem,
  IconButton,
  InputAdornment,
} from "@mui/material";

import Visibility from "@mui/icons-material/Visibility";
import VisibilityOff from "@mui/icons-material/VisibilityOff";
import { useAuth } from "../context/AuthContext";

export default function Signup() {
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [role, setRole] = useState("customer");

  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);

  const { register } = useAuth();
  const navigate = useNavigate();

  const onSubmit = async (e) => {
    e.preventDefault();

    setError("");
    setSuccess("");

    if (password !== confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    if (password.length < 6) {
      setError("Password must be at least 6 characters");
      return;
    }

    setLoading(true);

    // try {
    //   await register({
    //     full_name: fullName,
    //     email,
    //     password,
    //     role: "customer",
    //   });

    //   setSuccess("Account created successfully. Redirecting to login...");

    //   setTimeout(() => {
    //     navigate("/login");
    //   }, 1000);
    // } catch (err) {
    //   setError(
    //     err.response?.data?.detail ||
    //       err.response?.data?.message ||
    //       "Registration failed",
    //   );
    // } finally {
    //   setLoading(false);
    // }

    try {
  await register({
    full_name: fullName,
    email,
    password,
    role: "customer",
  });

  setSuccess(
    "Account created successfully. An OTP has been sent to your email."
  );

  setTimeout(() => {
    navigate(
      `/verify-email?email=${encodeURIComponent(
        email
      )}`
    );
  }, 1000);
} catch (err) {
  setError(
    err.response?.data?.detail ||
      err.response?.data?.message ||
      "Registration failed"
  );
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
        px: 2,
      }}
    >
      <Card
        sx={{
          width: 420,
          maxWidth: "100%",
          background: "rgba(255,255,255,0.06)",
          backdropFilter: "blur(18px)",
          border: "1px solid rgba(255,255,255,0.1)",
        }}
      >
        <CardContent sx={{ p: 3 }}>
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
            Create your customer account
          </Typography>

          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          {success && (
            <Alert severity="success" sx={{ mb: 2 }}>
              {success}
            </Alert>
          )}

          <Box component="form" onSubmit={onSubmit}>
            <TextField
              fullWidth
              label="Full Name"
              margin="normal"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              required
            />

            <TextField
              fullWidth
              type="email"
              label="Email"
              margin="normal"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />

            <TextField
              fullWidth
              select
              label="Role"
              margin="normal"
              value={role}
              onChange={(e) => setRole(e.target.value)}
            >
              <MenuItem value="customer">Customer</MenuItem>
              <MenuItem value="staff">Staff</MenuItem>
              <MenuItem value="admin">Admin</MenuItem>
            </TextField>

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

            <TextField
              fullWidth
              type={showConfirmPassword ? "text" : "password"}
              label="Confirm Password"
              margin="normal"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
              slotProps={{
                input: {
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton
                        onClick={() => setShowConfirmPassword((prev) => !prev)}
                        edge="end"
                        aria-label={
                          showConfirmPassword
                            ? "Hide confirm password"
                            : "Show confirm password"
                        }
                      >
                        {showConfirmPassword ? (
                          <VisibilityOff />
                        ) : (
                          <Visibility />
                        )}
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
              {loading ? "Creating Account..." : "Sign Up"}
            </Button>

            <Box
              sx={{
                mt: 2,
                display: "flex",
                justifyContent: "center",
                alignItems: "center",
                gap: 0.5,
              }}
            >
              <Typography variant="body2">Don't have an account ? </Typography>

              <Button
                variant="text"
                onClick={() => navigate("/login")}
                sx={{
                  minWidth: "auto",
                  p: 0,
                }}
              >
                Sign In
              </Button>
            </Box>
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
}
