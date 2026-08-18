import { useEffect, useState } from "react";
import {
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  Grid,
  TextField,
  Typography,
  Alert,
  CircularProgress,
  MenuItem,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Divider,
} from "@mui/material";

import api from "../api/client";
import { useAuth } from "../context/AuthContext";
import GlassCard from "../components/GlassCard";

export default function Products() {
  const { user } = useAuth();

  // ============================================================
  // PRODUCTS / CATEGORIES
  // ============================================================

  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);

  const [q, setQ] = useState("");
  const [categoryId, setCategoryId] = useState("");

  const [loading, setLoading] = useState(true);

  // ============================================================
  // MESSAGES
  // ============================================================

  const [msg, setMsg] = useState("");
  const [error, setError] = useState("");

  // ============================================================
  // CART
  // ============================================================

  const [cart, setCart] = useState([]);

  // ============================================================
  // ADD PRODUCT
  // ============================================================

  const [openAdd, setOpenAdd] = useState(false);
  const [adding, setAdding] = useState(false);

  const [productForm, setProductForm] = useState({
    name: "",
    description: "",
    category_id: "",
    price: "",
    sku: "",
    stock_quantity: "",
    status: "active",
  });

  const [imageFile, setImageFile] = useState(null);
  const [imagePreview, setImagePreview] = useState("");

  // ============================================================
  // EDIT PRODUCT
  // ============================================================

  const [openEdit, setOpenEdit] = useState(false);
  const [editingProduct, setEditingProduct] = useState(null);
  const [updating, setUpdating] = useState(false);

  const [editForm, setEditForm] = useState({
    name: "",
    description: "",
    category_id: "",
    price: "",
    sku: "",
    stock_quantity: "",
    status: "active",
  });

  const [editImageFile, setEditImageFile] = useState(null);
  const [editImagePreview, setEditImagePreview] = useState("");

  // ============================================================
  // ROLE CHECK
  // ============================================================

  const isStaff = user?.role === "admin" || user?.role === "staff";

  const isCustomer = user?.role === "customer";

  // ============================================================
  // API BASE URL
  // ============================================================

  const API_BASE_URL =
    import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

  // ============================================================
  // IMAGE URL HELPER
  // ============================================================

  const getImageUrl = (imagePath) => {
    if (!imagePath) {
      return "";
    }

    if (imagePath.startsWith("http://") || imagePath.startsWith("https://")) {
      return imagePath;
    }

    return `${API_BASE_URL}${imagePath}`;
  };

  // ============================================================
  // LOAD PRODUCTS
  // ============================================================

  const load = async () => {
    setLoading(true);

    try {
      const params = {};

      if (q.trim()) {
        params.search = q.trim();
      }

      if (categoryId) {
        params.category_id = categoryId;
      }

      const [productsResponse, categoriesResponse] = await Promise.all([
        api.get("/products", { params }),
        api.get("/categories"),
      ]);

      setProducts(productsResponse.data);
      setCategories(categoriesResponse.data);
    } catch (e) {
      setError(e.response?.data?.detail || "Failed to load products");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, [q, categoryId]);

  // ============================================================
  // PRODUCT FORM CHANGE
  // ============================================================

  const handleProductChange = (e) => {
    const { name, value } = e.target;

    setProductForm((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  // ============================================================
  // EDIT FORM CHANGE
  // ============================================================

  const handleEditChange = (e) => {
    const { name, value } = e.target;

    setEditForm((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  // ============================================================
  // IMAGE VALIDATION
  // ============================================================

  const validateImage = (file) => {
    const allowedTypes = ["image/jpeg", "image/png", "image/webp", "image/gif"];

    if (!allowedTypes.includes(file.type)) {
      return "Only JPEG, PNG, WEBP and GIF images are allowed";
    }

    const maxSize = 5 * 1024 * 1024;

    if (file.size > maxSize) {
      return "Image size must be less than 5 MB";
    }

    return null;
  };

  // ============================================================
  // ADD IMAGE CHANGE
  // ============================================================

  const handleImageChange = (e) => {
    const file = e.target.files?.[0];

    if (!file) {
      return;
    }

    const validationError = validateImage(file);

    if (validationError) {
      setError(validationError);
      e.target.value = "";
      return;
    }

    setError("");

    if (imagePreview) {
      URL.revokeObjectURL(imagePreview);
    }

    const previewUrl = URL.createObjectURL(file);

    setImageFile(file);
    setImagePreview(previewUrl);
  };

  // ============================================================
  // EDIT IMAGE CHANGE
  // ============================================================

  const handleEditImageChange = (e) => {
    const file = e.target.files?.[0];

    if (!file) {
      return;
    }

    const validationError = validateImage(file);

    if (validationError) {
      setError(validationError);
      e.target.value = "";
      return;
    }

    setError("");

    if (editImagePreview) {
      URL.revokeObjectURL(editImagePreview);
    }

    const previewUrl = URL.createObjectURL(file);

    setEditImageFile(file);
    setEditImagePreview(previewUrl);
  };

  // ============================================================
  // RESET ADD FORM
  // ============================================================

  const resetProductForm = () => {
    setProductForm({
      name: "",
      description: "",
      category_id: "",
      price: "",
      sku: "",
      stock_quantity: "",
      status: "active",
    });

    setImageFile(null);

    if (imagePreview) {
      URL.revokeObjectURL(imagePreview);
    }

    setImagePreview("");
  };

  // ============================================================
  // OPEN ADD PRODUCT
  // ============================================================

  const openAddProduct = () => {
    setError("");
    setMsg("");

    resetProductForm();

    setOpenAdd(true);
  };

  // ============================================================
  // ADD PRODUCT
  // ============================================================

  const handleAddProduct = async (e) => {
    e.preventDefault();

    setError("");
    setMsg("");
    setAdding(true);

    try {
      if (!productForm.name.trim()) {
        setError("Please enter product name");
        return;
      }

      if (!productForm.category_id) {
        setError("Please select a category");
        return;
      }

      if (!productForm.price) {
        setError("Please enter product price");
        return;
      }

      if (productForm.stock_quantity === "") {
        setError("Please enter stock quantity");
        return;
      }

      if (!productForm.sku.trim()) {
        setError("Please enter SKU");
        return;
      }

      // ------------------------------------------
      // CREATE PRODUCT
      // ------------------------------------------

      const payload = {
        name: productForm.name.trim(),

        description: productForm.description.trim() || null,

        category_id: Number(productForm.category_id),

        price: Number(productForm.price),

        sku: productForm.sku.trim(),

        stock_quantity: Number(productForm.stock_quantity),

        status: productForm.status,
      };

      const response = await api.post("/products", payload);

      const createdProduct = response.data;

      // ------------------------------------------
      // UPLOAD IMAGE
      // ------------------------------------------

      if (imageFile) {
        const formData = new FormData();

        formData.append("file", imageFile);

        await api.post(`/products/${createdProduct.id}/image`, formData);
      }

      // ------------------------------------------
      // SUCCESS
      // ------------------------------------------

      setMsg(
        imageFile
          ? "Product and image added successfully"
          : "Product added successfully",
      );

      setOpenAdd(false);

      resetProductForm();

      await load();
    } catch (e) {
      setError(e.response?.data?.detail || "Failed to add product");
    } finally {
      setAdding(false);
    }
  };

  // ============================================================
  // OPEN EDIT PRODUCT
  // ============================================================

  const openEditProduct = (product) => {
    setError("");
    setMsg("");

    setEditingProduct(product);

    setEditForm({
      name: product.name || "",

      description: product.description || "",

      category_id: product.category_id ?? "",

      price: product.price ?? "",

      sku: product.sku || "",

      stock_quantity: product.stock_quantity ?? product.current_stock ?? "",

      status: product.status || "active",
    });

    setEditImageFile(null);

    if (editImagePreview) {
      URL.revokeObjectURL(editImagePreview);
    }

    setEditImagePreview("");

    setOpenEdit(true);
  };

  // ============================================================
  // CLOSE EDIT PRODUCT
  // ============================================================

  const closeEditProduct = () => {
    if (updating) {
      return;
    }

    setOpenEdit(false);

    setEditingProduct(null);

    setEditImageFile(null);

    if (editImagePreview) {
      URL.revokeObjectURL(editImagePreview);
    }

    setEditImagePreview("");
  };

  // ============================================================
  // UPDATE PRODUCT
  // ============================================================

  const handleEditProduct = async (e) => {
    e.preventDefault();

    if (!editingProduct) {
      return;
    }

    setError("");
    setMsg("");
    setUpdating(true);

    try {
      if (!editForm.name.trim()) {
        setError("Please enter product name");
        return;
      }

      if (!editForm.category_id) {
        setError("Please select a category");
        return;
      }

      if (!editForm.price) {
        setError("Please enter product price");
        return;
      }

      if (!editForm.sku.trim()) {
        setError("Please enter SKU");
        return;
      }

      // ------------------------------------------
      // UPDATE PRODUCT DETAILS
      // ------------------------------------------

      const payload = {
        name: editForm.name.trim(),

        description: editForm.description.trim() || null,

        category_id: Number(editForm.category_id),

        price: Number(editForm.price),

        sku: editForm.sku.trim(),

        status: editForm.status,
      };

      await api.put(`/products/${editingProduct.id}`, payload);

      // ------------------------------------------
      // UPDATE IMAGE
      // ------------------------------------------

      if (editImageFile) {
        const formData = new FormData();

        formData.append("file", editImageFile);

        await api.post(`/products/${editingProduct.id}/image`, formData);
      }

      // ------------------------------------------
      // SUCCESS
      // ------------------------------------------

      setMsg(
        editImageFile
          ? "Product and image updated successfully"
          : "Product updated successfully",
      );

      closeEditProduct();

      await load();
    } catch (e) {
      setError(e.response?.data?.detail || "Failed to update product");
    } finally {
      setUpdating(false);
    }
  };

  // ============================================================
  // CART
  // ============================================================

  const addToCart = (product) => {
    setCart((prev) => {
      const existing = prev.find((item) => item.product_id === product.id);

      if (existing) {
        return prev.map((item) =>
          item.product_id === product.id
            ? {
                ...item,
                quantity: item.quantity + 1,
              }
            : item,
        );
      }

      return [
        ...prev,
        {
          product_id: product.id,

          name: product.name,

          price: product.price,

          quantity: 1,
        },
      ];
    });
  };

  // ============================================================
  // PLACE ORDER
  // ============================================================

  const placeOrder = async () => {
    if (!cart.length) {
      return;
    }

    setError("");
    setMsg("");

    try {
      await api.post("/orders", {
        items: cart.map((item) => ({
          product_id: item.product_id,

          quantity: item.quantity,
        })),
      });

      setCart([]);

      setMsg("Order placed successfully");

      await load();
    } catch (e) {
      setError(e.response?.data?.detail || "Order failed");
    }
  };

  // ============================================================
  // RENDER
  // ============================================================

  return (
    <Box>
      {/* ======================================================
          HEADER
      ====================================================== */}

      <Box
        display="flex"
        justifyContent="space-between"
        alignItems="center"
        mb={2}
        flexWrap="wrap"
        gap={2}
      >
        <Typography variant="h4" fontWeight={800}>
          Products
        </Typography>

        {isStaff && (
          <Button variant="contained" onClick={openAddProduct}>
            + Add Product
          </Button>
        )}
      </Box>

      {/* ======================================================
          MESSAGES
      ====================================================== */}

      {msg && (
        <Alert severity="success" sx={{ mb: 2 }} onClose={() => setMsg("")}>
          {msg}
        </Alert>
      )}

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError("")}>
          {error}
        </Alert>
      )}

      {/* ======================================================
          SEARCH
      ====================================================== */}

      <Box display="flex" gap={2} mb={3} flexWrap="wrap">
        <TextField
          size="small"
          label="Search"
          value={q}
          onChange={(e) => setQ(e.target.value)}
        />

        <TextField
          select
          size="small"
          label="Category"
          value={categoryId}
          onChange={(e) => setCategoryId(e.target.value)}
          sx={{
            minWidth: 160,
          }}
        >
          <MenuItem value="">All</MenuItem>

          {categories.map((category) => (
            <MenuItem key={category.id} value={category.id}>
              {category.name}
            </MenuItem>
          ))}
        </TextField>
      </Box>

      {/* ======================================================
          CUSTOMER CART
      ====================================================== */}

      {isCustomer && cart.length > 0 && (
        <GlassCard
          sx={{
            mb: 3,
            p: 2,
          }}
        >
          <Typography fontWeight={700}>
            Cart ({cart.reduce((sum, item) => sum + item.quantity, 0)})
          </Typography>

          {cart.map((item) => (
            <Typography key={item.product_id} variant="body2">
              {item.name} × {item.quantity} = ₹
              {(Number(item.price) * item.quantity).toFixed(2)}
            </Typography>
          ))}

          <Button variant="contained" sx={{ mt: 1 }} onClick={placeOrder}>
            Place Order
          </Button>
        </GlassCard>
      )}

      {/* ======================================================
          PRODUCTS
      ====================================================== */}

      {loading ? (
        <CircularProgress />
      ) : products.length === 0 ? (
        <Typography color="text.secondary">No products found.</Typography>
      ) : (
        <Grid container spacing={2}>
          {products.map((product) => (
            <Grid item xs={12} sm={6} md={4} lg={3} key={product.id}>
              <Card
                sx={{
                  height: "100%",
                  background: "rgba(255,255,255,0.04)",
                  border: "1px solid rgba(255,255,255,0.08)",
                  overflow: "hidden",
                }}
              >
                {/* IMAGE */}

                {product.image_path ? (
                  <Box
                    component="img"
                    src={getImageUrl(product.image_path)}
                    alt={product.name}
                    sx={{
                      width: "100%",
                      height: 180,
                      objectFit: "cover",
                      display: "block",
                    }}
                  />
                ) : (
                  <Box
                    sx={{
                      height: 180,
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      background: "rgba(255,255,255,0.04)",
                    }}
                  >
                    <Typography color="text.secondary">No Image</Typography>
                  </Box>
                )}

                <CardContent>
                  {/* NAME */}

                  <Typography fontWeight={700} noWrap>
                    {product.name}
                  </Typography>

                  {/* SKU */}

                  <Typography variant="body2" color="text.secondary" noWrap>
                    {product.sku}
                  </Typography>

                  {/* DESCRIPTION */}

                  {product.description && (
                    <Typography
                      variant="body2"
                      color="text.secondary"
                      sx={{
                        mt: 1,
                        display: "-webkit-box",
                        WebkitLineClamp: 2,
                        WebkitBoxOrient: "vertical",
                        overflow: "hidden",
                      }}
                    >
                      {product.description}
                    </Typography>
                  )}

                  {/* PRICE */}

                  <Typography variant="h6" color="secondary" mt={1}>
                    ₹{Number(product.price).toLocaleString()}
                  </Typography>

                  {/* STOCK */}

                  <Chip
                    size="small"
                    label={`Stock: ${
                      product.stock_quantity ?? product.current_stock ?? 0
                    }`}
                    sx={{
                      mt: 1,
                    }}
                  />

                  {/* STATUS */}

                  <Chip
                    size="small"
                    label={product.status}
                    sx={{
                      mt: 1,
                      ml: 1,
                    }}
                  />

                  {/* CUSTOMER */}

                  {isCustomer && (
                    <Button
                      fullWidth
                      size="small"
                      variant="outlined"
                      sx={{
                        mt: 1.5,
                      }}
                      onClick={() => addToCart(product)}
                      disabled={
                        Number(
                          product.stock_quantity ?? product.current_stock ?? 0,
                        ) <= 0
                      }
                    >
                      Add to cart
                    </Button>
                  )}

                  {/* ADMIN / STAFF */}

                  {isStaff && (
                    <Button
                      fullWidth
                      size="small"
                      variant="outlined"
                      sx={{
                        mt: 1.5,
                      }}
                      onClick={() => openEditProduct(product)}
                    >
                      Edit Product
                    </Button>
                  )}
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {/* ======================================================
          ADD PRODUCT DIALOG
      ====================================================== */}

      <Dialog
        open={openAdd}
        onClose={() => {
          if (!adding) {
            setOpenAdd(false);
            resetProductForm();
          }
        }}
        fullWidth
        maxWidth="sm"
        PaperProps={{
          sx: {
            background: "#111827",
            color: "#ffffff",
            border: "1px solid rgba(255,255,255,0.12)",
            borderRadius: 3,
            boxShadow: "0 25px 80px rgba(0,0,0,0.45)",
          },
        }}
      >
        <DialogTitle>Add New Product</DialogTitle>

        <Divider />

        <Box component="form" onSubmit={handleAddProduct}>
          <DialogContent>
            <TextField
              fullWidth
              required
              label="Product Name"
              name="name"
              margin="normal"
              value={productForm.name}
              onChange={handleProductChange}
            />

            <TextField
              fullWidth
              label="Description"
              name="description"
              margin="normal"
              multiline
              rows={3}
              value={productForm.description}
              onChange={handleProductChange}
            />

            <TextField
              fullWidth
              required
              select
              label="Category"
              name="category_id"
              margin="normal"
              value={productForm.category_id}
              onChange={handleProductChange}
            >
              {categories.map((category) => (
                <MenuItem key={category.id} value={category.id}>
                  {category.name}
                </MenuItem>
              ))}
            </TextField>

            <TextField
              fullWidth
              required
              type="number"
              label="Price"
              name="price"
              margin="normal"
              inputProps={{
                min: 0.01,
                step: "0.01",
              }}
              value={productForm.price}
              onChange={handleProductChange}
            />

            <TextField
              fullWidth
              required
              label="SKU"
              name="sku"
              margin="normal"
              value={productForm.sku}
              onChange={handleProductChange}
            />

            <TextField
              fullWidth
              required
              type="number"
              label="Stock Quantity"
              name="stock_quantity"
              margin="normal"
              inputProps={{
                min: 0,
              }}
              value={productForm.stock_quantity}
              onChange={handleProductChange}
            />

            <TextField
              fullWidth
              select
              label="Status"
              name="status"
              margin="normal"
              value={productForm.status}
              onChange={handleProductChange}
            >
              <MenuItem value="active">Active</MenuItem>

              <MenuItem value="inactive">Inactive</MenuItem>
            </TextField>

            {/* IMAGE */}

            {isStaff && (
              <Box mt={2}>
                <Typography variant="subtitle1" fontWeight={700} mb={1}>
                  Product Image
                </Typography>

                <Button variant="outlined" component="label" fullWidth>
                  {imageFile ? "Change Image" : "Choose Image"}

                  <input
                    hidden
                    type="file"
                    accept="image/jpeg,image/png,image/webp,image/gif"
                    onChange={handleImageChange}
                  />
                </Button>

                {imageFile && (
                  <Typography variant="body2" color="text.secondary" mt={1}>
                    Selected: {imageFile.name}
                  </Typography>
                )}

                {imagePreview && (
                  <Box mt={2}>
                    <Box
                      component="img"
                      src={imagePreview}
                      alt="Product preview"
                      sx={{
                        width: "100%",
                        maxHeight: 250,
                        objectFit: "contain",
                        borderRadius: 2,
                        border: "1px solid rgba(255,255,255,0.15)",
                      }}
                    />
                  </Box>
                )}

                <Typography
                  variant="caption"
                  color="text.secondary"
                  display="block"
                  mt={1}
                >
                  JPG, PNG, WEBP or GIF. Maximum 5 MB.
                </Typography>
              </Box>
            )}
          </DialogContent>

          <DialogActions sx={{ p: 2 }}>
            <Button
              onClick={() => {
                setOpenAdd(false);
                resetProductForm();
              }}
              disabled={adding}
            >
              Cancel
            </Button>

            <Button type="submit" variant="contained" disabled={adding}>
              {adding ? "Adding..." : "Add Product"}
            </Button>
          </DialogActions>
        </Box>
      </Dialog>

      {/* ======================================================
          EDIT PRODUCT DIALOG
      ====================================================== */}

      <Dialog
        open={openEdit}
        onClose={closeEditProduct}
        fullWidth
        maxWidth="sm"
        PaperProps={{
          sx: {
            background: "#111827",
            color: "#ffffff",
            border: "1px solid rgba(255,255,255,0.12)",
            borderRadius: 3,
            boxShadow: "0 25px 80px rgba(0,0,0,0.45)",
          },
        }}
      >
        <DialogTitle>Edit Product</DialogTitle>

        <Divider />

        <Box component="form" onSubmit={handleEditProduct}>
          <DialogContent>
            {/* NAME */}

            <TextField
              fullWidth
              required
              label="Product Name"
              name="name"
              margin="normal"
              value={editForm.name}
              onChange={handleEditChange}
            />

            {/* DESCRIPTION */}

            <TextField
              fullWidth
              label="Description"
              name="description"
              margin="normal"
              multiline
              rows={3}
              value={editForm.description}
              onChange={handleEditChange}
            />

            {/* CATEGORY */}

            <TextField
              fullWidth
              required
              select
              label="Category"
              name="category_id"
              margin="normal"
              value={editForm.category_id}
              onChange={handleEditChange}
            >
              {categories.map((category) => (
                <MenuItem key={category.id} value={category.id}>
                  {category.name}
                </MenuItem>
              ))}
            </TextField>

            {/* PRICE */}

            <TextField
              fullWidth
              required
              type="number"
              label="Price"
              name="price"
              margin="normal"
              inputProps={{
                min: 0.01,
                step: "0.01",
              }}
              value={editForm.price}
              onChange={handleEditChange}
            />

            {/* SKU */}

            <TextField
              fullWidth
              required
              label="SKU"
              name="sku"
              margin="normal"
              value={editForm.sku}
              onChange={handleEditChange}
            />

            {/* STOCK */}

            <TextField
              fullWidth
              type="number"
              label="Stock Quantity"
              name="stock_quantity"
              margin="normal"
              inputProps={{
                min: 0,
              }}
              value={editForm.stock_quantity}
              disabled
              helperText="Stock is managed from Inventory"
            />

            {/* STATUS */}

            <TextField
              fullWidth
              select
              label="Status"
              name="status"
              margin="normal"
              value={editForm.status}
              onChange={handleEditChange}
            >
              <MenuItem value="active">Active</MenuItem>

              <MenuItem value="inactive">Inactive</MenuItem>
            </TextField>

            {/* CURRENT IMAGE */}

            {editingProduct?.image_path && (
              <Box mt={2}>
                <Typography variant="subtitle1" fontWeight={700} mb={1}>
                  Current Image
                </Typography>

                <Box
                  component="img"
                  src={getImageUrl(editingProduct.image_path)}
                  alt={editingProduct.name}
                  sx={{
                    width: "100%",
                    maxHeight: 220,
                    objectFit: "contain",
                    borderRadius: 2,
                    border: "1px solid rgba(255,255,255,0.15)",
                  }}
                />
              </Box>
            )}

            {/* CHANGE IMAGE */}

            <Box mt={3}>
              <Typography variant="subtitle1" fontWeight={700} mb={1}>
                Change Product Image
              </Typography>

              <Button variant="outlined" component="label" fullWidth>
                {editImageFile ? "Change Selected Image" : "Choose New Image"}

                <input
                  hidden
                  type="file"
                  accept="image/jpeg,image/png,image/webp,image/gif"
                  onChange={handleEditImageChange}
                />
              </Button>

              {editImageFile && (
                <Typography variant="body2" color="text.secondary" mt={1}>
                  Selected: {editImageFile.name}
                </Typography>
              )}

              {editImagePreview && (
                <Box mt={2}>
                  <Typography variant="subtitle2" mb={1}>
                    New Image Preview
                  </Typography>

                  <Box
                    component="img"
                    src={editImagePreview}
                    alt="New product preview"
                    sx={{
                      width: "100%",
                      maxHeight: 250,
                      objectFit: "contain",
                      borderRadius: 2,
                      border: "1px solid rgba(255,255,255,0.15)",
                    }}
                  />
                </Box>
              )}

              <Typography
                variant="caption"
                color="text.secondary"
                display="block"
                mt={1}
              >
                JPG, PNG, WEBP or GIF. Maximum 5 MB.
              </Typography>
            </Box>
          </DialogContent>

          <DialogActions sx={{ p: 2 }}>
            <Button onClick={closeEditProduct} disabled={updating}>
              Cancel
            </Button>

            <Button type="submit" variant="contained" disabled={updating}>
              {updating ? "Updating..." : "Save Changes"}
            </Button>
          </DialogActions>
        </Box>
      </Dialog>
    </Box>
  );
}
