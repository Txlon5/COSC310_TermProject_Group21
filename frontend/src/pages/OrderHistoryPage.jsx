import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { getOrderHistory, getOrderById, getPaymentStatus, getRestaurants } from "../api";
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

export default function OrderHistoryPage() {
  const { user } = useAuth();
  const [orders, setOrders] = useState([]);
  const [restaurantMap, setRestaurantMap] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [expandedId, setExpandedId] = useState(null);
  const [detail, setDetail] = useState({});

  useEffect(() => {
    Promise.all([getOrderHistory(user.id), getRestaurants()])
      .then(([ords, restaurants]) => {
        setOrders(ords);
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
    </div>
  );
}
