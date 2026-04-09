import { useState, useEffect } from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faClock, faFire, faCheckCircle, faTruck, faBagShopping, faCircleCheck, faCircleXmark } from "@fortawesome/free-solid-svg-icons";
import {
  listAllUsers, updateUserById, deleteUserById,
  getRestaurants, createRestaurant, updateRestaurant, deleteRestaurant,
  getRestaurantMenu, addMenuItem, updateMenuItem, deleteMenuItem,
  getOrders, updateOrderStatus,
  getTransaction, updateTransaction,
} from "../api";

const TABS = ["Overview", "Users", "Orders", "Payments", "Restaurants"];

const STATUS_HERO = {
  created:   { icon: faClock,       label: "Order Placed",    color: "#1d4ed8", bg: "#dbeafe" },
  preparing: { icon: faFire,        label: "Being Prepared",  color: "#c2410c", bg: "#ffedd5" },
  ready:     { icon: faCheckCircle, label: "Ready",           color: "#7c3aed", bg: "#ede9fe" },
  delivered: { icon: faTruck,       label: "Delivered",       color: "#15803d", bg: "#dcfce7" },
  pickedup:  { icon: faBagShopping, label: "Picked Up",       color: "#15803d", bg: "#dcfce7" },
  completed: { icon: faCircleCheck, label: "Order Complete",  color: "#15803d", bg: "#dcfce7" },
  cancelled: { icon: faCircleXmark, label: "Order Cancelled", color: "#b91c1c", bg: "#fee2e2" },
};

const ORDER_STATUS_COLORS = {
  created:   "blue",
  preparing: "orange",
  ready:     "purple",
  delivered: "green",
  pickedup:  "green",
  completed: "green",
  cancelled: "red",
};

// Mirror the exact backend transition rules from orders_service.py
const PICKUP_TRANSITIONS = {
  created:   ["preparing", "cancelled"],
  preparing: ["ready",     "cancelled"],
  ready:     ["pickedup",  "cancelled"],
  pickedup:  ["completed"],
  delivered: [],
  completed: [],
  cancelled: [],
};
const DELIVERY_TRANSITIONS = {
  created:   ["preparing", "cancelled"],
  preparing: ["ready",     "cancelled"],
  ready:     ["delivered", "cancelled"],
  delivered: ["completed"],
  pickedup:  [],
  completed: [],
  cancelled: [],
};

function nextStatuses(order) {
  const map = order.delivery_method === "pickup" ? PICKUP_TRANSITIONS : DELIVERY_TRANSITIONS;
  return map[order.status] ?? [];
}

export default function AdminPage() {
  const [tab, setTab] = useState("Overview");

  return (
    <div className="page-container">
      <h2>Admin Panel</h2>
      <div className="admin-tabs">
        {TABS.map((t) => (
          <button
            key={t}
            className={`admin-tab ${tab === t ? "active" : ""}`}
            onClick={() => setTab(t)}
          >
            {t}
          </button>
        ))}
      </div>
      <div className="admin-tab-content">
        {tab === "Overview"    && <OverviewTab onNavigate={setTab} />}
        {tab === "Users"       && <UsersTab />}
        {tab === "Orders"      && <OrdersTab />}
        {tab === "Payments"    && <PaymentsTab />}
        {tab === "Restaurants" && <RestaurantsTab />}
      </div>
    </div>
  );
}

/* ── Overview Tab ──────────────────────────────────────── */
function OverviewTab({ onNavigate }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([listAllUsers(), getRestaurants(), getOrders()])
      .then(([users, restaurants, orders]) => setData({ users, restaurants, orders }))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="loading">Loading overview…</div>;
  if (error) return <div className="alert error">{error}</div>;

  const { users, restaurants, orders } = data;
  const openCount = restaurants.filter((r) => r.isOpen).length;
  const revenue = orders.reduce((sum, o) => sum + (o.total_price || 0), 0);
  const activeOrders = orders.filter((o) => !["completed", "cancelled"].includes(o.status));
  const recentOrders = [...orders]
    .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
    .slice(0, 5);

  return (
    <div>
      <div className="overview-stats">
        <div className="stat-card" role="button" style={{ cursor: "pointer" }} onClick={() => onNavigate("Users")}>
          <span className="stat-value">{users.length}</span>
          <span className="stat-label">Total Users</span>
        </div>
        <div className="stat-card" role="button" style={{ cursor: "pointer" }} onClick={() => onNavigate("Restaurants")}>
          <span className="stat-value">{restaurants.length}</span>
          <span className="stat-label">Restaurants</span>
          <span className="stat-sub">{openCount} open now</span>
        </div>
        <div className="stat-card" role="button" style={{ cursor: "pointer" }} onClick={() => onNavigate("Orders")}>
          <span className="stat-value">{orders.length}</span>
          <span className="stat-label">Total Orders</span>
          <span className="stat-sub">{activeOrders.length} active</span>
        </div>
        <div className="stat-card" role="button" style={{ cursor: "pointer" }} onClick={() => onNavigate("Payments")}>
          <span className="stat-value">${revenue.toFixed(2)}</span>
          <span className="stat-label">Total Revenue</span>
        </div>
      </div>

      <div className="overview-grid">
        <div className="card">
          <h3 className="overview-section-title">Recent Orders</h3>
          {recentOrders.length === 0 ? (
            <p className="empty-state">No orders yet.</p>
          ) : (
            recentOrders.map((o) => (
              <div key={o.order_id} className="overview-order-row">
                <div className="overview-order-left">
                  <span className={`status-badge ${ORDER_STATUS_COLORS[o.status] || "gray"}`}>{o.status}</span>
                  <span className="overview-order-method">{o.delivery_method}</span>
                </div>
                <div className="overview-order-right">
                  {o.total_price != null && <span>${o.total_price.toFixed(2)}</span>}
                  <span className="overview-order-date">
                    {new Date(o.created_at).toLocaleDateString(undefined, { month: "short", day: "numeric" })}
                  </span>
                </div>
              </div>
            ))
          )}
        </div>

        <div className="card">
          <h3 className="overview-section-title">Restaurants</h3>
          {restaurants.map((r) => (
            <div key={r.restaurant_id} className="overview-restaurant-row">
              <span className="overview-restaurant-name">{r.restaurant_name}</span>
              <div className="overview-restaurant-right">
                {r.opening_time && r.closing_time && (
                  <span className="admin-restaurant-hours">{r.opening_time} – {r.closing_time}</span>
                )}
                <span className={`status-badge ${r.isOpen ? "open" : "closed"}`}>
                  {r.isOpen ? "Open" : "Closed"}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

/* ── Users Tab ──────────────────────────────────────────── */
function UsersTab() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [editId, setEditId] = useState(null);
  const [form, setForm] = useState({ name: "", email: "", password: "" });
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    listAllUsers()
      .then(setUsers)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  const openEdit = (u) => {
    setEditId(u.id);
    setForm({ name: u.name, email: u.email, password: "" });
  };
  const closeEdit = () => { setEditId(null); setForm({ name: "", email: "", password: "" }); };

  const handleSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError("");
    try {
      const payload = { ...form, password: form.password.trim() || null };
      const updated = await updateUserById(editId, payload);
      setUsers((u) => u.map((x) => (x.id === editId ? updated : x)));
      closeEdit();
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Delete this user permanently?")) return;
    try {
      await deleteUserById(id);
      setUsers((u) => u.filter((x) => x.id !== id));
    } catch (err) {
      setError(err.message);
    }
  };

  if (loading) return <div className="loading">Loading users…</div>;

  return (
    <div>
      {error && <div className="alert error">{error}</div>}
      <p className="admin-count">{users.length} user(s) total</p>
      <div className="order-list">
        {users.map((u) => {
          const isOpen = editId === u.id;
          return (
            <div key={u.id} className={`order-card-wrap ${isOpen ? "expanded" : ""}`}>
              <div
                className="order-card"
                role="button"
                tabIndex={0}
                onClick={() => isOpen ? closeEdit() : openEdit(u)}
                onKeyDown={(e) => e.key === "Enter" && (isOpen ? closeEdit() : openEdit(u))}
                style={{ cursor: "pointer", userSelect: "none" }}
              >
                <div className="order-card-top">
                  <span className="order-id">{u.name}</span>
                  <div style={{ display: "flex", alignItems: "center", gap: "0.6rem" }}>
                    <span className={`role-pill ${u.role}`}>{u.role}</span>
                    <span className="order-chevron">{isOpen ? "▲" : "▼"}</span>
                  </div>
                </div>
                <div className="admin-card-divider" />
                <div className="admin-card-meta">
                  <span className="admin-order-email">{u.email}</span>
                  <span className="id-cell">UserID: {u.id}</span>
                </div>
              </div>
              {isOpen && (
                <div className="order-detail-panel">
                  <form onSubmit={handleSave}>
                    <div className="admin-expand-cols">
                      <div className="admin-expand-card">
                        <div className="form-group" style={{ margin: 0 }}>
                          <label>Name</label>
                          <input type="text" value={form.name} onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))} required />
                        </div>
                      </div>
                      <div className="admin-expand-card">
                        <div className="form-group" style={{ margin: 0 }}>
                          <label>Email</label>
                          <input type="email" value={form.email} onChange={(e) => setForm((f) => ({ ...f, email: e.target.value }))} required />
                        </div>
                      </div>
                      <div className="admin-expand-card">
                        <div className="form-group" style={{ margin: 0 }}>
                          <label>New Password</label>
                          <input type="password" value={form.password} onChange={(e) => setForm((f) => ({ ...f, password: e.target.value }))} placeholder="Leave blank to keep" />
                        </div>
                      </div>
                    </div>
                    <div className="form-actions" style={{ marginTop: "1rem" }}>
                      <button className="btn btn-primary btn-sm" disabled={saving}>{saving ? "Saving…" : "Save"}</button>
                      <button type="button" className="btn btn-sm btn-danger" onClick={() => handleDelete(u.id)}>Delete</button>
                    </div>
                  </form>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

/* ── Orders Tab ─────────────────────────────────────────── */
function OrdersTab() {
  const [orders, setOrders] = useState([]);
  const [userMap, setUserMap] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [updating, setUpdating] = useState(null);
  const [expandedId, setExpandedId] = useState(null);

  const [restaurantMap, setRestaurantMap] = useState({});

  useEffect(() => {
    Promise.all([getOrders(), listAllUsers(), getRestaurants()])
      .then(([ords, users, restaurants]) => {
        setOrders([...ords].sort((a, b) => (b.created_at > a.created_at ? 1 : -1)));
        setUserMap(Object.fromEntries(users.map((u) => [u.id, u.email])));
        setRestaurantMap(Object.fromEntries(restaurants.map((r) => [r.restaurant_id, r.restaurant_name])));
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  const handleStatusChange = async (orderId, newStatus) => {
    setUpdating(orderId);
    setError("");
    try {
      const updated = await updateOrderStatus(orderId, newStatus);
      setOrders((prev) => prev.map((o) => (o.order_id === orderId ? updated : o)));
    } catch (err) {
      setError(err.message);
    } finally {
      setUpdating(null);
    }
  };

  if (loading) return <div className="loading">Loading orders…</div>;

  return (
    <div>
      {error && <div className="alert error">{error}</div>}
      <p className="admin-count">{orders.length} order(s) total</p>
      <div className="order-list">
        {orders.map((o) => {
          const isOpen = expandedId === o.order_id;
          const next = nextStatuses(o);
          const busy = updating === o.order_id;
          return (
            <div key={o.order_id} className={`order-card-wrap ${isOpen ? "expanded" : ""}`}>
              {/* Summary row */}
              <div
                className="order-card"
                role="button"
                tabIndex={0}
                onClick={() => setExpandedId(isOpen ? null : o.order_id)}
                onKeyDown={(e) => e.key === "Enter" && setExpandedId(isOpen ? null : o.order_id)}
                style={{ cursor: "pointer", userSelect: "none" }}
              >
                <div className="order-card-top">
                  <span className="admin-order-email">User: {userMap[o.user_id] ?? o.user_id.slice(0, 8) + "…"}</span>
                  <span className="admin-order-email" style={{ color: "#111", textAlign: "center", fontWeight: 700 }}>{new Date(o.created_at).toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" })}</span>
                  <div style={{ display: "flex", alignItems: "center", gap: "0.6rem" }}>
                    <span className={`status-badge ${ORDER_STATUS_COLORS[o.status] || "gray"}`}>{o.status}</span>
                    <span className="order-chevron">{isOpen ? "▲" : "▼"}</span>
                  </div>
                </div>
                <div className="admin-card-restaurant">
                  {restaurantMap[o.restaurant_id] ?? "—"}
                </div>
                <div className="admin-card-divider" />
                <div className="admin-card-meta">
                  <span className="id-cell">Order: #{o.order_id}</span>
                  <div style={{ display: "flex", gap: "0.75rem", alignItems: "center" }}>
                    <span className="admin-card-type">Type: <strong>{o.delivery_method}</strong></span>
                    {o.total_price != null && <span className="admin-card-total">Total: <strong>${o.total_price.toFixed(2)}</strong></span>}
                  </div>
                </div>
              </div>

              {/* Expanded detail */}
              {isOpen && (
                <div className="order-detail-panel">
                  {/* Hero */}
                  {(() => { const hero = STATUS_HERO[o.status] ?? STATUS_HERO.created; return (
                    <div className="order-status-hero" style={{ background: hero.bg, color: hero.color, marginBottom: "1.25rem" }}>
                      <FontAwesomeIcon icon={hero.icon} className="order-status-hero-icon" />
                      <span className="order-status-hero-label">{hero.label}</span>
                    </div>
                  ); })()}
                  {/* Items table */}
                  <div className="order-detail-block" style={{ marginBottom: "1.25rem" }}>
                    <h4 className="order-detail-block-title">Items</h4>
                    <table className="order-items-table">
                      <colgroup><col /><col /><col /></colgroup>
                      <thead>
                        <tr>
                          <th>Item</th>
                          <th className="order-items-th-center">Qty</th>
                          <th className="order-items-th-right">Price</th>
                        </tr>
                      </thead>
                      <tbody>
                        {o.items.map((item, i) => (
                          <tr key={i}>
                            <td className="order-items-td-name">{item.name}</td>
                            <td className="order-items-td-center">{item.quantity}</td>
                            <td className="order-items-td-right">${(item.price * item.quantity).toFixed(2)}</td>
                          </tr>
                        ))}
                      </tbody>
                      <tfoot>
                        <tr>
                          <td colSpan={2} className="order-items-tf-label">Total</td>
                          <td className="order-items-tf-total">{o.total_price != null ? `$${o.total_price.toFixed(2)}` : "—"}</td>
                        </tr>
                      </tfoot>
                    </table>
                  </div>

                  {/* Delivery + Advance Status row */}
                  <div className="order-detail-row">
                    <div className="order-detail-block">
                      <h4 className="order-detail-block-title">Delivery</h4>
                      <dl className="order-detail-dl">
                        <dt>Method</dt><dd style={{ textTransform: "capitalize" }}>{o.delivery_method}</dd>
                        {o.delivery_address && <><dt>Address</dt><dd>{o.delivery_address}</dd></>}
                        {o.pickup_location  && <><dt>Pickup</dt><dd>{o.pickup_location}</dd></>}
                        {o.assigned_driver  && <><dt>Driver</dt><dd>{o.assigned_driver}</dd></>}
                        <dt>Placed</dt><dd>{new Date(o.created_at).toLocaleString(undefined, { month: "short", day: "numeric", year: "numeric", hour: "numeric", minute: "2-digit" })}</dd>
                        <dt>Order ID</dt><dd className="id-cell" style={{ wordBreak: "break-all" }}>{o.order_id}</dd>
                      </dl>
                    </div>
                    {next.length > 0 && (
                      <div className="order-detail-block">
                        <h4 className="order-detail-block-title">Advance Status</h4>
                        <div className="status-actions">
                          {next.map((s) => (
                            <button
                              key={s}
                              className={`btn btn-sm ${s === "cancelled" ? "btn-danger" : "btn-outline"}`}
                              disabled={busy}
                              onClick={() => handleStatusChange(o.order_id, s)}
                            >
                              {busy ? "…" : `→ ${s}`}
                            </button>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

/* ── Payments Tab ───────────────────────────────────────── */
const PAYMENT_STATUSES = ["pending", "approved", "declined", "refunded"];

function PaymentsTab() {
  const [orders, setOrders] = useState([]);
  const [userMap, setUserMap] = useState({});
  const [restaurantMap, setRestaurantMap] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [payments, setPayments] = useState({});  // order_id → { payment, loading, error }
  const [updating, setUpdating] = useState(null);
  const [expandedId, setExpandedId] = useState(null);

  useEffect(() => {
    Promise.all([getOrders(), listAllUsers(), getRestaurants()])
      .then(([ords, users, restaurants]) => {
        setOrders([...ords].sort((a, b) => (b.created_at > a.created_at ? 1 : -1)));
        setUserMap(Object.fromEntries(users.map((u) => [u.id, u.email])));
        setRestaurantMap(Object.fromEntries(restaurants.map((r) => [r.restaurant_id, r.restaurant_name])));
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  const handleToggle = async (orderId) => {
    if (expandedId === orderId) { setExpandedId(null); return; }
    setExpandedId(orderId);
    if (payments[orderId]) return;
    setPayments((p) => ({ ...p, [orderId]: { loading: true } }));
    try {
      const payment = await getTransaction(orderId);
      setPayments((p) => ({ ...p, [orderId]: { payment, loading: false } }));
    } catch (err) {
      setPayments((p) => ({ ...p, [orderId]: { loading: false, error: err.message } }));
    }
  };

  const handleUpdatePayment = async (orderId, newStatus, orderStatus) => {
    if (
      newStatus === "approved" &&
      orderStatus !== "created" &&
      !window.confirm(
        `Warning: Approving payment automatically advances the order to "preparing".\n` +
        `This order is currently "${orderStatus}", not "created".\n\n` +
        `The approval will likely fail. Proceed anyway?`
      )
    ) return;

    setUpdating(orderId);
    setError("");
    try {
      const updated = await updateTransaction(orderId, { status: newStatus });
      setPayments((p) => ({ ...p, [orderId]: { ...p[orderId], payment: updated } }));
      if (newStatus === "approved") getOrders().then(setOrders).catch(() => {});
    } catch (err) {
      const msg = err.message.includes("Unable to update order status to approved")
        ? `Cannot approve: order must be in "created" state (currently "${orderStatus}").`
        : err.message;
      setError(msg);
    } finally {
      setUpdating(null);
    }
  };

  if (loading) return <div className="loading">Loading orders…</div>;

  return (
    <div>
      {error && <div className="alert error">{error}</div>}
      <p className="admin-count">{orders.length} order(s) — click a row to load payment</p>
      <div className="order-list">
        {orders.map((o) => {
          const isOpen = expandedId === o.order_id;
          const row = payments[o.order_id];
          const busy = updating === o.order_id;
          return (
            <div key={o.order_id} className={`order-card-wrap ${isOpen ? "expanded" : ""}`}>
              {/* Summary row */}
              <div
                className="order-card"
                role="button"
                tabIndex={0}
                onClick={() => handleToggle(o.order_id)}
                onKeyDown={(e) => e.key === "Enter" && handleToggle(o.order_id)}
                style={{ cursor: "pointer", userSelect: "none" }}
              >
                <div className="order-card-top">
                  <span className="admin-order-email">User: {userMap[o.user_id] ?? o.user_id.slice(0, 8) + "…"}</span>
                  <span className="admin-order-email" style={{ color: "#111", textAlign: "center", fontWeight: 700 }}>{new Date(o.created_at).toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" })}</span>
                  <div style={{ display: "flex", alignItems: "center", gap: "0.6rem" }}>
                    <span className={`status-badge ${ORDER_STATUS_COLORS[o.status] || "gray"}`}>{o.status}</span>
                    {row?.payment && (
                      <span className={`payment-status-badge ${row.payment.status}`}>{row.payment.status}</span>
                    )}
                    <span className="order-chevron">{isOpen ? "▲" : "▼"}</span>
                  </div>
                </div>
                <div className="admin-card-restaurant">
                  {restaurantMap[o.restaurant_id] ?? "—"}
                </div>
                <div className="admin-card-divider" />
                <div className="admin-card-meta">
                  <span className="id-cell">Order: #{o.order_id}</span>
                  <div style={{ display: "flex", gap: "0.75rem", alignItems: "center" }}>
                    <span className="admin-card-type">Type: <strong>{o.delivery_method}</strong></span>
                    {o.total_price != null && <span className="admin-card-total">Total: <strong>${o.total_price.toFixed(2)}</strong></span>}
                  </div>
                </div>
              </div>

              {/* Expanded payment detail */}
              {isOpen && (
                <div className="order-detail-panel">
                  {!row || row.loading ? (
                    <div className="loading" style={{ padding: "0.5rem 0" }}>Loading payment…</div>
                  ) : row.error ? (
                    <div className="alert error">{row.error}</div>
                  ) : (
                    <div className="admin-expand-cols">
                      <div className="admin-expand-card">
                        <h4>Payment Details</h4>
                        <dl className="detail-list">
                          <dt>Card</dt><dd>•••• {row.payment.card?.card_num?.slice(-4)}</dd>
                          <dt>Holder</dt><dd>{row.payment.card?.holder_name}</dd>
                          <dt>Amount</dt><dd>${row.payment.price_total?.toFixed(2)}</dd>
                          <dt>Updated</dt><dd>{new Date(row.payment.updated_at).toLocaleString()}</dd>
                          <dt>Payment ID</dt><dd className="id-cell" style={{ fontSize: "0.75rem", wordBreak: "break-all" }}>{row.payment.payment_id}</dd>
                        </dl>
                      </div>
                      {row.payment.status === "pending" && (
                        <div className="admin-expand-card">
                          <h4>Update Status</h4>
                          <p style={{ fontSize: "0.82rem", color: "#888", marginBottom: "0.75rem" }}>
                            Current: <span className={`payment-status-badge ${row.payment.status}`}>{row.payment.status}</span>
                          </p>
                          <div className="status-actions">
                            {PAYMENT_STATUSES.filter((s) => s !== row.payment.status).map((s) => (
                              <button
                                key={s}
                                className={`btn btn-sm ${s === "approved" ? "btn-success" : s === "declined" ? "btn-danger" : "btn-outline"}`}
                                disabled={busy}
                                title={s === "approved" && o.status !== "created" ? `Order is "${o.status}" — approval requires "created" state` : ""}
                                onClick={() => handleUpdatePayment(o.order_id, s, o.status)}
                              >
                                {busy ? "…" : s}
                              </button>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

/* ── Restaurants Tab ────────────────────────────────────── */
function RestaurantsTab() {
  const [restaurants, setRestaurants] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [editId, setEditId] = useState(null);
  const [form, setForm] = useState({ restaurant_name: "", isOpen: true, tags: "", opening_time: "", closing_time: "" });
  const [saving, setSaving] = useState(false);
  const [expandedId, setExpandedId] = useState(null);

  useEffect(() => {
    getRestaurants()
      .then(setRestaurants)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  const setF = (field) => (e) =>
    setForm((f) => ({ ...f, [field]: field === "isOpen" ? e.target.checked : e.target.value }));

  const openAdd = () => { setEditId(null); setForm({ restaurant_name: "", isOpen: true, tags: "", opening_time: "", closing_time: "" }); setShowForm(true); };
  const openEdit = (r) => {
    setEditId(r.restaurant_id);
    setForm({ restaurant_name: r.restaurant_name, isOpen: r.isOpen, tags: r.tags.join(", "), opening_time: r.opening_time || "", closing_time: r.closing_time || "" });
    setShowForm(true);
  };
  const closeForm = () => { setShowForm(false); setEditId(null); };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      const payload = {
        restaurant_name: form.restaurant_name,
        isOpen: form.isOpen,
        tags: form.tags.split(",").map((t) => t.trim()).filter(Boolean),
        opening_time: form.opening_time,
        closing_time: form.closing_time,
      };
      if (editId) {
        const updated = await updateRestaurant(editId, payload);
        setRestaurants((r) => r.map((x) => (x.restaurant_id === editId ? updated : x)));
      } else {
        const created = await createRestaurant(payload);
        setRestaurants((r) => [...r, created]);
      }
      closeForm();
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Delete this restaurant?")) return;
    try {
      await deleteRestaurant(id);
      setRestaurants((r) => r.filter((x) => x.restaurant_id !== id));
      if (expandedId === id) setExpandedId(null);
    } catch (err) {
      setError(err.message);
    }
  };

  if (loading) return <div className="loading">Loading restaurants…</div>;

  return (
    <div>
      {error && <div className="alert error">{error}</div>}
      <div className="admin-section-header">
        <p className="admin-count">{restaurants.length} restaurant(s)</p>
        <button className="btn btn-primary btn-sm" onClick={openAdd}>+ Add Restaurant</button>
      </div>

      {showForm && !editId && (
        <div className="card admin-form-card">
          <h3>New Restaurant</h3>
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label>Name</label>
              <input type="text" value={form.restaurant_name} onChange={setF("restaurant_name")} required />
            </div>
            <div className="form-group">
              <label>Tags (comma-separated)</label>
              <input type="text" value={form.tags} onChange={setF("tags")} placeholder="pizza, italian, fast-food" />
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>Opening Time</label>
                <input type="time" value={form.opening_time} onChange={setF("opening_time")} required />
              </div>
              <div className="form-group">
                <label>Closing Time</label>
                <input type="time" value={form.closing_time} onChange={setF("closing_time")} required />
              </div>
            </div>
            <div className="form-group">
              <label className="checkbox-label">
                <input type="checkbox" checked={form.isOpen} onChange={setF("isOpen")} /> Active
              </label>
              <p className="hint">Uncheck to temporarily close this restaurant regardless of its business hours.</p>
            </div>
            <div className="form-actions">
              <button className="btn btn-primary" disabled={saving}>{saving ? "Saving…" : "Save"}</button>
              <button type="button" className="btn btn-outline" onClick={closeForm}>Cancel</button>
            </div>
          </form>
        </div>
      )}

      <div className="admin-restaurant-list">
        {restaurants.map((r) => (
          <div key={r.restaurant_id} className="admin-restaurant-row">
            <div className="admin-restaurant-header">
              <div className="admin-restaurant-info">
                <span className="admin-restaurant-name">{r.restaurant_name}</span>
                <span className={`status-badge ${r.isOpen ? "open" : "closed"}`}>{r.isOpen ? "Open" : "Closed"}</span>
                {r.opening_time && r.closing_time && (
                  <span className="admin-restaurant-hours">{r.opening_time} – {r.closing_time}</span>
                )}
                <div className="tags">
                  {r.tags.map((t) => <span key={t} className="tag">{t}</span>)}
                </div>
              </div>
              <div className="admin-restaurant-actions">
                <button className="btn btn-sm btn-outline" onClick={() => setExpandedId(expandedId === r.restaurant_id ? null : r.restaurant_id)}>
                  {expandedId === r.restaurant_id ? "Hide Menu" : "Menu"}
                </button>
                <button className="btn btn-sm btn-outline" onClick={() => openEdit(r)}>Edit</button>
                <button className="btn btn-sm btn-danger" onClick={() => handleDelete(r.restaurant_id)}>Delete</button>
              </div>
            </div>
            {editId === r.restaurant_id && showForm && (
              <div className="card admin-form-card" style={{ margin: "0.75rem 0 0" }}>
                <h3>Edit Restaurant</h3>
                <form onSubmit={handleSubmit}>
                  <div className="form-group">
                    <label>Name</label>
                    <input type="text" value={form.restaurant_name} onChange={setF("restaurant_name")} required />
                  </div>
                  <div className="form-group">
                    <label>Tags (comma-separated)</label>
                    <input type="text" value={form.tags} onChange={setF("tags")} placeholder="pizza, italian, fast-food" />
                  </div>
                  <div className="form-row">
                    <div className="form-group">
                      <label>Opening Time</label>
                      <input type="time" value={form.opening_time} onChange={setF("opening_time")} />
                    </div>
                    <div className="form-group">
                      <label>Closing Time</label>
                      <input type="time" value={form.closing_time} onChange={setF("closing_time")} />
                    </div>
                  </div>
                  <div className="form-group">
                    <label className="checkbox-label">
                      <input type="checkbox" checked={form.isOpen} onChange={setF("isOpen")} /> Active
                    </label>
                    <p className="hint">Uncheck to temporarily close this restaurant regardless of its business hours.</p>
                  </div>
                  <div className="form-actions">
                    <button className="btn btn-primary" disabled={saving}>{saving ? "Saving…" : "Save"}</button>
                    <button type="button" className="btn btn-outline" onClick={closeForm}>Cancel</button>
                  </div>
                </form>
              </div>
            )}
            {expandedId === r.restaurant_id && (
              <MenuManager restaurantId={r.restaurant_id} />
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

/* ── Menu Manager (inline) ──────────────────────────────── */
function MenuManager({ restaurantId }) {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [editItem, setEditItem] = useState(null);
  const [form, setForm] = useState({ name: "", price: "", category: "" });
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    getRestaurantMenu(restaurantId)
      .then(setItems)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [restaurantId]);

  const setF = (field) => (e) => setForm((f) => ({ ...f, [field]: e.target.value }));

  const openAdd = () => { setEditItem(null); setForm({ name: "", price: "", category: "" }); setShowForm(true); };
  const openEdit = (item) => { setEditItem(item); setForm({ name: item.name, price: String(item.price), category: item.category }); setShowForm(true); };
  const closeForm = () => { setShowForm(false); setEditItem(null); };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      const payload = { name: form.name, price: parseFloat(form.price), category: form.category };
      if (editItem) {
        const updated = await updateMenuItem(restaurantId, editItem.menuItemId, payload);
        setItems((prev) => prev.map((i) => (i.menuItemId === editItem.menuItemId ? updated : i)));
      } else {
        const created = await addMenuItem(restaurantId, payload);
        setItems((prev) => [...prev, created]);
      }
      closeForm();
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (menuItemId) => {
    if (!window.confirm("Delete this menu item?")) return;
    try {
      await deleteMenuItem(restaurantId, menuItemId);
      setItems((prev) => prev.filter((i) => i.menuItemId !== menuItemId));
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="menu-manager">
      {error && <div className="alert error">{error}</div>}
      <div className="menu-manager-header">
        <span className="menu-manager-title">Menu Items ({loading ? "…" : items.length})</span>
        <button className="btn btn-sm btn-primary" onClick={openAdd}>+ Add Item</button>
      </div>

      {showForm && (
        <form className="menu-item-form" onSubmit={handleSubmit}>
          <input type="text" placeholder="Name" value={form.name} onChange={setF("name")} required />
          <input type="number" placeholder="Price" step="0.01" min="0.01" value={form.price} onChange={setF("price")} required />
          <input type="text" placeholder="Category" value={form.category} onChange={setF("category")} required />
          <button className="btn btn-primary btn-sm" disabled={saving}>{saving ? "…" : "Save"}</button>
          <button type="button" className="btn btn-outline btn-sm" onClick={closeForm}>Cancel</button>
        </form>
      )}

      {!loading && items.length === 0 && <p className="empty-state" style={{ fontSize: "0.85rem" }}>No menu items.</p>}
      {items.map((item) => (
        <div key={item.menuItemId} className="menu-manager-item">
          <span className="menu-item-name">{item.name}</span>
          <span className="tag">{item.category}</span>
          <span className="menu-item-price">${item.price.toFixed(2)}</span>
          <button className="btn btn-sm btn-outline" onClick={() => openEdit(item)}>Edit</button>
          <button className="btn btn-sm btn-danger" onClick={() => handleDelete(item.menuItemId)}>Delete</button>
        </div>
      ))}
    </div>
  );
}
