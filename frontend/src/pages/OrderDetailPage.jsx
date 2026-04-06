import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { getOrderById, updateOrderStatus, getPaymentStatus } from "../api";
import { useAuth } from "../useAuth";
import OrderDetail from "../components/OrderDetail";

const PICKUP_TRANSITIONS = {
  created:   ["preparing", "cancelled"],
  preparing: ["ready",     "cancelled"],
  ready:     ["pickedup",  "cancelled"],
  pickedup:  ["completed"],
  delivered: [], completed: [], cancelled: [],
};
const DELIVERY_TRANSITIONS = {
  created:   ["preparing", "cancelled"],
  preparing: ["ready",     "cancelled"],
  ready:     ["delivered", "cancelled"],
  delivered: ["completed"],
  pickedup:  [], completed: [], cancelled: [],
};

const STATUS_COLORS = {
  created: "blue", preparing: "orange", ready: "purple",
  delivered: "green", pickedup: "green", completed: "green", cancelled: "red",
};

export default function OrderDetailPage() {
  const { id } = useParams();
  const { user } = useAuth();
  const [order, setOrder] = useState(null);
  const [payment, setPayment] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [statusLoading, setStatusLoading] = useState(false);

  useEffect(() => {
    Promise.all([getOrderById(id), getPaymentStatus(id).catch(() => null)])
      .then(([o, p]) => { setOrder(o); setPayment(p); })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [id]);

  const handleStatusChange = async (newStatus) => {
    setStatusLoading(true);
    try {
      const updated = await updateOrderStatus(id, newStatus);
      setOrder(updated);
    } catch (err) {
      setError(err.message);
    } finally {
      setStatusLoading(false);
    }
  };

  if (loading) return <div className="loading">Loading order…</div>;
  if (error) return <div className="page-container"><div className="alert error">{error}</div></div>;
  if (!order) return null;

  const transitions = order.delivery_method === "pickup" ? PICKUP_TRANSITIONS : DELIVERY_TRANSITIONS;
  const nextStatuses = user.role === "admin" ? (transitions[order.status] ?? []) : [];

  return (
    <div className="page-container">
      <div className="order-detail-header">
        <div className="order-detail-header-left">
          <Link to="/orders" className="order-detail-back">← Orders</Link>
          <h2>Order Detail</h2>
          <span className="id-cell" style={{ fontSize: "0.8rem" }}>#{order.order_id}</span>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
          <span className="order-detail-date">{new Date(order.created_at).toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" })}</span>
          <span className={`status-badge large ${STATUS_COLORS[order.status] || "gray"}`}>{order.status}</span>
        </div>
      </div>

      {error && <div className="alert error">{error}</div>}

      <div className="card" style={{ padding: "1.25rem" }}>
        <OrderDetail
          order={order}
          payment={payment}
          nextStatuses={nextStatuses}
          onStatusChange={handleStatusChange}
          statusBusy={statusLoading}
        />
      </div>
    </div>
  );
}
