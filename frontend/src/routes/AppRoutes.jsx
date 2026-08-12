import { Navigate, Route, Routes } from "react-router-dom";
import AppShell from "../components/AppShell";
import Dashboard from "../pages/Dashboard";
import Products from "../pages/Products";
import Categories from "../pages/Categories";
import Inventory from "../pages/Inventory";
import Orders from "../pages/Orders";
import Notifications from "../pages/Notifications";
import Login from "../pages/Login";
import { useAuth } from "../context/AuthContext";

function Protected() {
  const { user } = useAuth();
  return user ? <AppShell /> : <Navigate to="/login" replace />;
}

export default function AppRoutes() {
  return <Routes>
    <Route path="/login" element={<Login />} />
    <Route element={<Protected />}>
      <Route path="/" element={<Dashboard />} />
      <Route path="/products" element={<Products />} />
      <Route path="/categories" element={<Categories />} />
      <Route path="/inventory" element={<Inventory />} />
      <Route path="/orders" element={<Orders />} />
      <Route path="/notifications" element={<Notifications />} />
    </Route>
    <Route path="*" element={<Navigate to="/" replace />} />
  </Routes>;
}
