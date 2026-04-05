const BASE = "/api";

function getToken() {
  return localStorage.getItem("token");
}

function authHeaders(extra = {}) {
  const token = getToken();
  return {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...extra,
  };
}

async function request(method, path, body, formData = false) {
  const opts = { method };
  if (formData) {
    opts.body = body;
  } else if (body !== undefined) {
    opts.headers = authHeaders();
    opts.body = JSON.stringify(body);
  } else {
    opts.headers = authHeaders();
  }

  const res = await fetch(`${BASE}${path}`, opts);
  if (res.status === 204) return null;
  const json = await res.json();
  if (!res.ok) {
    const detail = json.detail;
    const msg = Array.isArray(detail)
      ? detail.map((e) => e.msg || JSON.stringify(e)).join("; ")
      : detail || "Request failed";
    throw new Error(msg);
  }
  return json;
}

// Auth
export const login = (username, password) => {
  const form = new URLSearchParams();
  form.append("username", username);
  form.append("password", password);
  return request("POST", "/auth/login", form, true);
};

// Users
export const registerUser = (payload) => request("POST", "/users", payload);
export const getSelf = () => request("GET", "/users/self");
export const updateSelf = (payload) => request("PUT", "/users/self", payload);
export const deleteSelf = () => request("DELETE", "/users/self");

// Restaurants
export const getRestaurants = (params = {}) => {
  const qs = new URLSearchParams(
    Object.entries(params).filter(([, v]) => v !== undefined && v !== null && v !== "")
  ).toString();
  return request("GET", `/restaurants${qs ? `?${qs}` : ""}`);
};
export const getRestaurantById = (id) => request("GET", `/restaurants/${id}`);

// Menus
export const getRestaurantMenu = (restaurantId) =>
  request("GET", `/restaurants/${restaurantId}/menu`);

// Orders
export const createOrder = (payload) => request("POST", "/orders", payload);
export const getOrders = () => request("GET", "/orders/");
export const getOrderById = (id) => request("GET", `/orders/${id}`);
export const getOrderHistory = (userId) =>
  request("GET", `/orders/history/${userId}`);
export const updateOrderStatus = (id, status) =>
  request("PATCH", `/orders/${id}/status`, { status });
export const updateDeliveryInfo = (id, payload) =>
  request("PUT", `/orders/${id}/delivery`, payload);

// Payment Methods (Cards)
export const getMyCards = () => request("GET", "/payments/cards");
export const addCard = (payload) => request("POST", "/payments/cards", payload);
export const updateCard = (id, payload) =>
  request("PUT", `/payments/cards/${id}`, payload);
export const deleteCard = (id) => request("DELETE", `/payments/cards/${id}`);

// Transactions
export const getTransaction = (orderId) =>
  request("GET", `/payments/${orderId}`);
export const getPaymentStatus = (orderId) =>
  request("GET", `/payments/status/${orderId}`);
export const updateTransaction = (orderId, payload) =>
  request("PUT", `/payments/${orderId}`, payload);

// Notifications
export const getNotifications = (userId) =>
  request("GET", `/notifications/${userId}`);

// Admin
export const listAllUsers = () => request("GET", "/users");
export const updateUserById = (id, payload) => request("PUT", `/users/${id}`, payload);
export const deleteUserById = (id) => request("DELETE", `/users/${id}`);
export const createRestaurant = (payload) => request("POST", "/restaurants", payload);
export const updateRestaurant = (id, payload) => request("PUT", `/restaurants/${id}`, payload);
export const deleteRestaurant = (id) => request("DELETE", `/restaurants/${id}`);
export const addMenuItem = (restaurantId, payload) =>
  request("POST", `/restaurants/${restaurantId}/menu-item/add`, payload);
export const updateMenuItem = (restaurantId, itemId, payload) =>
  request("PUT", `/restaurants/${restaurantId}/menu/${itemId}`, payload);
export const deleteMenuItem = (restaurantId, itemId) =>
  request("DELETE", `/restaurants/${restaurantId}/menu/${itemId}`);
