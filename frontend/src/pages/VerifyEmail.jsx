import { useEffect, useState } from "react";
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  TextField,
  Typography,
} from "@mui/material";
import { useLocation, useNavigate } from "react-router-dom";

import { useAuth } from "../context/AuthContext";

export default function VerifyEmail() {
  const location = useLocation();
  const navigate = useNavigate();

  const {
    verifyEmail,
    sendOTP,
  } = useAuth();

  const queryEmail = new URLSearchParams(
    location.search
  ).get("email");

  const [email, setEmail] = useState(
    queryEmail || ""
  );

  const [code, setCode] = useState("");

  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const [loading, setLoading] = useState(false);
  const [resending, setResending] = useState(false);

  const [countdown, setCountdown] =
    useState(0);

  // ============================================================
  // COUNTDOWN
  // ============================================================

  useEffect(() => {
    if (countdown <= 0) return;

    const timer = setInterval(() => {
      setCountdown((prev) =>
        prev > 0 ? prev - 1 : 0
      );
    }, 1000);

    return () => clearInterval(timer);
  }, [countdown]);

  // ============================================================
  // VERIFY OTP
  // ============================================================

  const handleVerify = async (e) => {
    e.preventDefault();

    setError("");
    setSuccess("");

    if (!email.trim()) {
      setError("Please enter your email");
      return;
    }

    if (!/^\d{6}$/.test(code)) {
      setError(
        "Please enter a valid 6-digit OTP"
      );
      return;
    }

    setLoading(true);

    try {
      await verifyEmail(
        email.trim(),
        code
      );

      setSuccess(
        "Email verified successfully. Redirecting to login..."
      );

      setTimeout(() => {
        navigate("/login", {
          replace: true,
        });
      }, 1200);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          "Invalid or expired OTP"
      );
    } finally {
      setLoading(false);
    }
  };

  // ============================================================
  // RESEND OTP
  // ============================================================

  const handleResend = async () => {
    setError("");
    setSuccess("");

    if (!email.trim()) {
      setError("Please enter your email");
      return;
    }

    setResending(true);

    try {
      await sendOTP(email.trim());

      setSuccess(
        "A new OTP has been sent to your email."
      );

      setCode("");

      // 60 second resend cooldown
      setCountdown(60);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          "Failed to send OTP"
      );
    } finally {
      setResending(false);
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
          background:
            "rgba(255,255,255,0.06)",
          backdropFilter: "blur(18px)",
          border:
            "1px solid rgba(255,255,255,0.1)",
        }}
      >
        <CardContent sx={{ p: 3 }}>
          <Typography
            variant="h4"
            fontWeight={900}
            textAlign="center"
            gutterBottom
          >
            Verify
            <span
              style={{
                color: "#22d3ee",
              }}
            >
              Email
            </span>
          </Typography>

          <Typography
            variant="body2"
            color="text.secondary"
            textAlign="center"
            mb={3}
          >
            Enter the 6-digit OTP sent to
            your email address.
          </Typography>

          {error && (
            <Alert
              severity="error"
              sx={{ mb: 2 }}
            >
              {error}
            </Alert>
          )}

          {success && (
            <Alert
              severity="success"
              sx={{ mb: 2 }}
            >
              {success}
            </Alert>
          )}

          <Box
            component="form"
            onSubmit={handleVerify}
          >
            <TextField
              fullWidth
              type="email"
              label="Email"
              margin="normal"
              value={email}
              onChange={(e) =>
                setEmail(e.target.value)
              }
              required
            />

            <TextField
              fullWidth
              label="6-Digit OTP"
              margin="normal"
              value={code}
              onChange={(e) => {
                const value =
                  e.target.value
                    .replace(/\D/g, "")
                    .slice(0, 6);

                setCode(value);
              }}
              inputProps={{
                maxLength: 6,
                inputMode: "numeric",
              }}
              required
            />

            <Button
              fullWidth
              type="submit"
              variant="contained"
              size="large"
              sx={{ mt: 2 }}
              disabled={
                loading ||
                code.length !== 6
              }
            >
              {loading
                ? "Verifying..."
                : "Verify Email"}
            </Button>
          </Box>

          <Button
            fullWidth
            variant="text"
            sx={{ mt: 2 }}
            onClick={handleResend}
            disabled={
              resending ||
              countdown > 0
            }
          >
            {resending
              ? "Sending..."
              : countdown > 0
              ? `Resend OTP in ${countdown}s`
              : "Resend OTP"}
          </Button>

          <Button
            fullWidth
            variant="text"
            onClick={() =>
              navigate("/login")
            }
            sx={{ mt: 1 }}
          >
            Back to Login
          </Button>
        </CardContent>
      </Card>
    </Box>
  );
}