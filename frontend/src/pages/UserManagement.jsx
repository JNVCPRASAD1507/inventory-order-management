import { useEffect, useState } from "react";
import {
  Alert,
  Box,
  Chip,
  Paper,
  Tab,
  Tabs,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Typography,
  Button,
} from "@mui/material";

import api from "../api/client";

export default function UserManagement() {
  const [tab, setTab] = useState("all");
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const loadUsers = async () => {
    setLoading(true);
    setError("");

    try {
      let endpoint = "/users";

      if (tab === "customers") {
        endpoint = "/users/customers";
      }

      if (tab === "staff") {
        endpoint = "/users/staff";
      }

      const response = await api.get(endpoint);

      setUsers(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to load users");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadUsers();
  }, [tab]);

  const handleStatusChange = async (user) => {
  try {
    await api.patch(`/users/${user.id}/status`, {
      is_active: !user.is_active,
    });

    loadUsers();
  } catch (err) {
    setError(
      err.response?.data?.detail ||
        "Failed to update user status"
    );
  }
};

  return (
    <Box>
      <Typography variant="h4" fontWeight={800} mb={1}>
        User Management
      </Typography>

      <Typography variant="body2" color="text.secondary" mb={3}>
        Manage customers and staff members.
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Paper
        sx={{
          background: "rgba(255,255,255,0.04)",
          borderRadius: 3,
        }}
      >
        <Tabs
          value={tab}
          onChange={(event, value) => setTab(value)}
          sx={{ px: 2 }}
        >
          <Tab value="all" label="All Users" />

          <Tab value="customers" label="Customers" />

          <Tab value="staff" label="Staff" />
        </Tabs>

        <Table>
          <TableHead>
            <TableRow>
              <TableCell>ID</TableCell>
              <TableCell>Name</TableCell>
              <TableCell>Email</TableCell>
              <TableCell>Role</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Action</TableCell>
            </TableRow>
          </TableHead>

          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell colSpan={5} align="center">
                  Loading users...
                </TableCell>
              </TableRow>
            ) : users.length === 0 ? (
              <TableRow>
                <TableCell colSpan={5} align="center">
                  No users found
                </TableCell>
              </TableRow>
            ) : (
              users.map((user) => (
                <TableRow key={user.id}>
                  <TableCell>{user.id}</TableCell>

                  <TableCell>{user.full_name}</TableCell>

                  <TableCell>{user.email}</TableCell>

                  <TableCell>
                    <Chip
                      size="small"
                      label={user.role}
                      color={
                        user.role === "admin"
                          ? "error"
                          : user.role === "staff"
                            ? "warning"
                            : "primary"
                      }
                    />
                  </TableCell>

                  <TableCell>
                    <Chip
                      size="small"
                      label={user.is_active ? "Active" : "Inactive"}
                      color={user.is_active ? "success" : "default"}
                    />
                  </TableCell>

                  <TableCell>
                    {user.role !== "admin" && (
                      <Button
                        size="small"
                        variant="outlined"
                        color={user.is_active ? "error" : "success"}
                        onClick={() => handleStatusChange(user)}
                      >
                        {user.is_active ? "Deactivate" : "Activate"}
                      </Button>
                    )}
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </Paper>
    </Box>
  );
}
