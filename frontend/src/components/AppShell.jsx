import { useEffect, useState } from "react";
import { Outlet, useNavigate } from "react-router-dom";
import {
  AppBar,
  Box,
  Drawer,
  IconButton,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Toolbar,
  Typography,
  Avatar,
  Divider,
  Badge,
  useMediaQuery,
  useTheme,
} from "@mui/material";
import DashboardRoundedIcon from "@mui/icons-material/DashboardRounded";
import Inventory2RoundedIcon from "@mui/icons-material/Inventory2Rounded";
import CategoryRoundedIcon from "@mui/icons-material/CategoryRounded";
import ShoppingCartRoundedIcon from "@mui/icons-material/ShoppingCartRounded";
import NotificationsRoundedIcon from "@mui/icons-material/NotificationsRounded";
import LogoutRoundedIcon from "@mui/icons-material/LogoutRounded";
import MenuRoundedIcon from "@mui/icons-material/MenuRounded";
import PeopleRoundedIcon from "@mui/icons-material/PeopleRounded";
import { useAuth } from "../context/AuthContext";
import api from "../api/client";

const menu = [
  { label: "Dashboard", path: "/", icon: DashboardRoundedIcon },
  { label: "Products", path: "/products", icon: Inventory2RoundedIcon },
  { label: "Categories", path: "/categories", icon: CategoryRoundedIcon },
  {
    label: "Inventory",
    path: "/inventory",
    icon: Inventory2RoundedIcon,
    roles: ["admin", "staff"],
  },
  { label: "Orders", path: "/orders", icon: ShoppingCartRoundedIcon },
  {
    label: "Notifications",
    path: "/notifications",
    icon: NotificationsRoundedIcon,
  },
  // {
  //   label: "Users",
  //   path: "/users",
  //   icon: PeopleRoundedIcon,
  //   roles: ["admin"],
  // },
  {
    label: "User Management",
    path: "/users",
    icon: PeopleRoundedIcon,
    roles: ["admin"],
  },
];

export default function AppShell() {
  const [open, setOpen] = useState(true);
  const [unreadCount, setUnreadCount] = useState(0);
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const theme = useTheme();
  const mobile = useMediaQuery(theme.breakpoints.down("md"));

  useEffect(() => {
    const loadUnreadCount = async () => {
      try {
        const response = await api.get("/notifications");

        const unread = response.data.filter(
          (notification) => !notification.is_read,
        ).length;

        setUnreadCount(unread);
      } catch (error) {
        console.error("Failed to load notifications:", error);
      }
    };

    // Load immediately
    loadUnreadCount();

    // Refresh every 30 seconds
    const interval = setInterval(loadUnreadCount, 30000);

    // Cleanup when AppShell unmounts
    return () => clearInterval(interval);
  }, []);

  const content = (
    <Box sx={{ width: 260, p: 1.5 }}>
      <Box p={2} mb={1}>
        <Typography variant="h6" fontWeight={900}>
          Inventory<span style={{ color: "#22d3ee" }}>OS</span>
        </Typography>
        <Typography variant="caption" color="text.secondary">
          Operations command center
        </Typography>
      </Box>
      <List>
        {menu
          .filter(
            ({ roles }) => !roles || roles.includes(user?.role?.toLowerCase()),
          )
          .map(({ label, path, icon: Icon }) => (
            <ListItemButton
              key={path}
              onClick={() => navigate(path)}
              sx={{ borderRadius: 3, mb: 0.5 }}
            >
              <ListItemIcon>
                <Icon />
              </ListItemIcon>
              <ListItemText primary={label} />
            </ListItemButton>
          ))}
      </List>
      <Divider sx={{ my: 2 }} />
      <ListItemButton onClick={logout} sx={{ borderRadius: 3 }}>
        <ListItemIcon>
          <LogoutRoundedIcon />
        </ListItemIcon>
        <ListItemText primary="Sign out" />
      </ListItemButton>
    </Box>
  );

  return (
    <Box
      sx={{
        minHeight: "100vh",
        background:
          "radial-gradient(circle at 10% 0%, rgba(139,92,246,.18), transparent 28%), radial-gradient(circle at 90% 10%, rgba(34,211,238,.12), transparent 25%), #080d19",
      }}
    >
      <AppBar
        position="fixed"
        elevation={0}
        sx={{
          background: "rgba(8,13,25,.72)",
          backdropFilter: "blur(16px)",
          borderBottom: "1px solid rgba(255,255,255,.08)",
        }}
      >
        <Toolbar>
          {mobile && (
            <IconButton onClick={() => setOpen(!open)}>
              <MenuRoundedIcon />
            </IconButton>
          )}

          <Box sx={{ flexGrow: 1 }} />

          {/* Notification Bell */}
          <IconButton onClick={() => navigate("/notifications")} sx={{ mr: 1 }}>
            <Badge
              badgeContent={unreadCount}
              color="error"
              invisible={unreadCount === 0}
            >
              <NotificationsRoundedIcon />
            </Badge>
          </IconButton>

          <Typography mr={1} variant="body2">
            {user?.full_name}
          </Typography>

          <Avatar sx={{ width: 34, height: 34 }}>{user?.full_name?.[0]}</Avatar>
        </Toolbar>
      </AppBar>
      {mobile ? (
        <Drawer open={open} onClose={() => setOpen(false)}>
          {content}
        </Drawer>
      ) : (
        <Drawer variant="permanent" open>
          {content}
        </Drawer>
      )}
      <Box
        component="main"
        sx={{ ml: mobile ? 0 : "260px", pt: 10, px: { xs: 2, md: 4 }, pb: 5 }}
      >
        <Outlet />
      </Box>
    </Box>
  );
}
