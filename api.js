/**
 * Smart Online X — API client
 *
 * IMPORTANT: set API_BASE_URL to wherever you deploy the Flask backend
 * (Render, Railway, Fly.io, PythonAnywhere, etc). GitHub Pages only serves
 * static files, so the backend must be hosted separately.
 */
const API_BASE_URL = window.SMART_X_API_BASE || "http://localhost:5000";

function authToken() {
  return localStorage.getItem("sx_token");
}

function setAuthToken(token) {
  if (token) localStorage.setItem("sx_token", token);
  else localStorage.removeItem("sx_token");
}

function currentUser() {
  const raw = localStorage.getItem("sx_user");
  return raw ? JSON.parse(raw) : null;
}

function setCurrentUser(user) {
  if (user) localStorage.setItem("sx_user", JSON.stringify(user));
  else localStorage.removeItem("sx_user");
}

function logout() {
  setAuthToken(null);
  setCurrentUser(null);
  window.location.href = "index.html";
}

async function apiRequest(path, { method = "GET", body, auth = false } = {}) {
  const headers = { "Content-Type": "application/json" };
  if (auth) {
    const token = authToken();
    if (!token) {
      window.location.href = "login.html";
      throw new Error("Not authenticated");
    }
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });

  let data = null;
  try {
    data = await response.json();
  } catch (_) {
    /* no body */
  }

  if (!response.ok) {
    const message = (data && data.error) || `Request failed (${response.status})`;
    throw new Error(message);
  }
  return data;
}

const api = {
  signup: (payload) => apiRequest("/api/auth/signup", { method: "POST", body: payload }),
  login: (payload) => apiRequest("/api/auth/login", { method: "POST", body: payload }),
  me: () => apiRequest("/api/auth/me", { auth: true }),

  listProducts: (params = {}) => {
    const qs = new URLSearchParams(params).toString();
    return apiRequest(`/api/products${qs ? `?${qs}` : ""}`);
  },
  getProduct: (id) => apiRequest(`/api/products/${id}`),

  getCart: () => apiRequest("/api/cart", { auth: true }),
  addToCart: (productId, quantity = 1) =>
    apiRequest("/api/cart", { method: "POST", auth: true, body: { product_id: productId, quantity } }),
  updateCartItem: (itemId, quantity) =>
    apiRequest(`/api/cart/${itemId}`, { method: "PUT", auth: true, body: { quantity } }),
  removeCartItem: (itemId) => apiRequest(`/api/cart/${itemId}`, { method: "DELETE", auth: true }),

  checkout: (shippingAddress) =>
    apiRequest("/api/checkout", { method: "POST", auth: true, body: { shipping_address: shippingAddress } }),
  listOrders: () => apiRequest("/api/orders", { auth: true }),
  getOrder: (id) => apiRequest(`/api/orders/${id}`, { auth: true }),
};
