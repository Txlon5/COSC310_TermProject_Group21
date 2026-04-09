import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { getOrderHistory, getOrderById, getPaymentStatus, getRestaurants, getMyCards, reorderPastOrder } from "../api";
import { useAuth } from "../useAuth";
import OrderDetail from "../components/OrderDetail";

const STATUS_COLORS = {
  created:   "blue",
  preparing: "orange",
  ready:     "purple",
  delivered: "green",
  pickedup:  "green",
  completed: "green",
  cancelled: "red",
};

function ReorderModal({ order, onClose, onSuccess }) {
  const [cards, setCards] = useState([]);
  const [cardId, setCardId] = useState("");
  const [deliveryMethod, setDeliveryMethod] = useState(order.delivery_method || "delivery");
  const [deliveryAddress, setDeliveryAddress] = useState(order.delivery_address || "");
  const [pickupLocation, setPickupLocation] = useState(order.pickup_location || "");
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");

  useEffect(() => {
    getMyCards()
      .then((c) => { setCards(c); if (c.length > 0) setCardId(c[0].id); })
      .catch(() => setErr("Could not load payment cards."));
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!cardId) { setErr("Please select a payment card."); return; }
    setBusy(true);
    setErr("");
    try {
      const payload = { card_id: cardId, delivery_method: deliveryMethod };
      if (deliveryMethod === "delivery") payload.delivery_address = deliveryAddress;
      else payload.pickup_location = pickupLocation;
      const result = await reorderPastOrder(order.order_id, payload);
      onSuccess(result.order_id);
    } catch (e) {
      setErr(e.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="reorder-overlay" onClick={(e) => e.target === e.currentTarget && onClose()}>
      <div className="reorder-modal">
        <div className="reorder-modal-header">
          <span>Reorder #{order.order_id.slice(0, 8)}</span>
          <button className="reorder-modal-close" onClick={onClose}>✕</button>
        </div>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Payment Card</label>
            <select value={cardId} onChange={(e) => setCardId(e.target.value)} required>
              {cards.length === 0 && <option value="">No cards on file</option>}
              {cards.map((c) => (
                <option key={c.id} value={c.id}>
                  •••• {c.card_num?.slice(-4)} — {c.holder_name}
                </option>
              ))}
            </select>
          </div>
          <div className="form-group">
            <label>Delivery Method</label>
            <select value={deliveryMethod} onChange={(e) => setDeliveryMethod(e.target.value)}>
              <option value="delivery">Delivery</option>
              <option value="pickup">Pickup</option>
            </select>
          </div>
          {deliveryMethod === "delivery" ? (
            <div className="form-group">
              <label>Delivery Address</label>
              <input
                type="text"
                value={deliveryAddress}
                onChange={(e) => setDeliveryAddress(e.target.value)}
                placeholder="123 Main St"
                required
              />
            </div>
          ) : (
            <div className="form-group">
              <label>Pickup Location</label>
              <input
                type="text"
                value={pickupLocation}
                onChange={(e) => setPickupLocation(e.target.value)}
                placeholder="Pickup location"
              />
            </div>
          )}
          {err && <div className="alert error" style={{ marginBottom: "0.75rem" }}>{err}</div>}
          <div className="form-actions">
            <button type="submit" className="btn btn-primary w-full" disabled={busy || cards.length === 0}>
              {busy ? "Placing…" : "Place Order"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default function OrderHistoryPage() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [orders, setOrders] = useState([]);
  const [restaurantMap, setRestaurantMap] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [expandedId, setExpandedId] = useState(null);
  const [detail, setDetail] = useState({});
  const [reorderTarget, setReorderTarget] = useState(null);

  useEffect(() => {
    Promise.all([getOrderHistory(user.id), getRestaurants()])
      .then(([ords, restaurants]) => {
        setOrders([...ords].sort((a, b) => new Date(b.created_at) - new Date(a.created_at)));
        setRestaurantMap(Object.fromEntries(restaurants.map((r) => [r.restaurant_id, r.restaurant_name])));
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [user.id]);

  const handleToggle = async (orderId) => {
    if (expandedId === orderId) { setExpandedId(null); return; }
    setExpandedId(orderId);
    if (detail[orderId]) return;

    setDetail((d) => ({ ...d, [orderId]: { loading: true } }));
    try {
      const [order, payment] = await Promise.all([
        getOrderById(orderId),
        getPaymentStatus(orderId).catch(() => null),
      ]);
      setDetail((d) => ({ ...d, [orderId]: { order, payment, loading: false } }));
    } catch (err) {
      setDetail((d) => ({ ...d, [orderId]: { loading: false, error: err.message } }));
    }
  };

  if (loading) return <div className="loading">Loading orders…</div>;

  return (
    <div className="page-container">
      <h2>Order History</h2>
      {error && <div className="alert error">{error}</div>}
{orders.length === 0 ? (
        <p className="empty-state">No orders yet. <Link to="/">Browse restaurants</Link></p>
      ) : (
        <div className="order-list">
          {orders.map((order) => {
            const isOpen = expandedId === order.order_id;
            const row = detail[order.order_id];
            return (
              <div key={order.order_id} className={`order-card-wrap ${isOpen ? "expanded" : ""}`}>
                <div
                  className="order-card"
                  role="button"
                  tabIndex={0}
                  onClick={() => handleToggle(order.order_id)}
                  onKeyDown={(e) => e.key === "Enter" && handleToggle(order.order_id)}
                  style={{ cursor: "pointer", userSelect: "none" }}
                >
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div className="order-card-top">
                      <span className="order-id">Order: #{order.order_id.slice(0, 8)}</span>
                      <span style={{ color: "#111", fontWeight: 700 }}>
                        {new Date(order.created_at).toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" })}
                      </span>
                      <div style={{ display: "flex", alignItems: "center", gap: "0.6rem" }}>
                        <span className={`status-badge ${STATUS_COLORS[order.status] || "gray"}`}>{order.status}</span>
                        <span className="order-chevron">{isOpen ? "▲" : "▼"}</span>
                      </div>
                    </div>
                    <div className="admin-card-restaurant">
                      {restaurantMap[order.restaurant_id] ?? "—"}
                    </div>
                    <div className="admin-card-divider" />
                    <div className="admin-card-meta">
                      <span className="admin-card-type">Type: <strong>{order.delivery_method}</strong></span>
                      <span style={{ fontSize: "0.82rem", color: "#888" }}>{order.items.length} item{order.items.length !== 1 ? "s" : ""}</span>
                      {order.total_price != null && <span className="admin-card-total">Total: <strong>${order.total_price.toFixed(2)}</strong></span>}
                    </div>
                  </div>
                  {(order.status === "completed" || order.status === "delivered" || order.status === "pickedup") && (
                    <button
                      className="reorder-btn"
                      title="Reorder"
                      onClick={(e) => { e.stopPropagation(); setReorderTarget(order); }}
                    >+</button>
                  )}
                </div>

                {isOpen && (
                  <div className="order-detail-panel">
                    {!row || row.loading ? (
                      <div className="loading" style={{ padding: "1rem" }}>Loading details…</div>
                    ) : row.error ? (
                      <div className="alert error">{row.error}</div>
                    ) : (
                      <OrderDetail order={row.order} payment={row.payment} />
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
      {reorderTarget && (
        <ReorderModal
          order={reorderTarget}
          onClose={() => setReorderTarget(null)}
          onSuccess={(newOrderId) => navigate(`/orders/${newOrderId}`)}
        />
      )}
    </div>
  );
}
