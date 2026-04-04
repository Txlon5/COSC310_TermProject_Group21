import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faClock, faFire, faCheckCircle, faTruck, faBagShopping,
  faCircleCheck, faCircleXmark,
} from "@fortawesome/free-solid-svg-icons";

const STATUS_TIMELINE        = ["created", "preparing", "ready", "delivered", "completed"];
const STATUS_TIMELINE_PICKUP = ["created", "preparing", "ready", "pickedup",  "completed"];

const STATUS_HERO = {
  created:   { icon: faClock,       label: "Order Placed",    color: "#1d4ed8", bg: "#dbeafe" },
  preparing: { icon: faFire,        label: "Being Prepared",  color: "#c2410c", bg: "#ffedd5" },
  ready:     { icon: faCheckCircle, label: "Ready",           color: "#7c3aed", bg: "#ede9fe" },
  delivered: { icon: faTruck,       label: "Delivered",       color: "#15803d", bg: "#dcfce7" },
  pickedup:  { icon: faBagShopping, label: "Picked Up",       color: "#15803d", bg: "#dcfce7" },
  completed: { icon: faCircleCheck, label: "Order Complete",  color: "#15803d", bg: "#dcfce7" },
  cancelled: { icon: faCircleXmark, label: "Order Cancelled", color: "#b91c1c", bg: "#fee2e2" },
};

function fmtDate(str) {
  return new Date(str).toLocaleString(undefined, {
    month: "short", day: "numeric", year: "numeric",
    hour: "numeric", minute: "2-digit",
  });
}

export default function OrderDetail({ order, payment, nextStatuses, onStatusChange, statusBusy }) {
  const timeline = order.delivery_method === "pickup"
    ? STATUS_TIMELINE_PICKUP
    : STATUS_TIMELINE;

  const currentIdx  = timeline.indexOf(order.status);
  const isCancelled = order.status === "cancelled";
  const hero = STATUS_HERO[order.status] ?? STATUS_HERO.created;

  return (
    <div className="order-detail-inner">

      {/* ── Hero ── */}
      <div className="order-status-hero" style={{ background: hero.bg, color: hero.color }}>
        <FontAwesomeIcon icon={hero.icon} className="order-status-hero-icon" />
        <span className="order-status-hero-label">{hero.label}</span>
      </div>

      {/* ── Timeline ── */}
      <div className="order-timeline-wrap">
        {isCancelled ? (
          <div className="timeline-cancelled">Order cancelled</div>
        ) : (
          <div className="order-timeline">
            {timeline.map((s, i) => (
              <div key={s} className={`timeline-step ${i < currentIdx ? "done" : i === currentIdx ? "active" : "pending"}`}>
                <div className="timeline-dot" />
                {i < timeline.length - 1 && <div className="timeline-line" />}
                <span className="timeline-label">{s}</span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* ── Items ── */}
      <div className="order-detail-block">
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
            {order.items.map((item, i) => (
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
              <td className="order-items-tf-total">${order.total_price?.toFixed(2) ?? "—"}</td>
            </tr>
          </tfoot>
        </table>
      </div>

      {/* ── Delivery + Payment row ── */}
      <div className="order-detail-row">
        <div className="order-detail-block">
          <h4 className="order-detail-block-title">Delivery</h4>
          <dl className="order-detail-dl">
            <dt>Method</dt>
            <dd style={{ textTransform: "capitalize" }}>{order.delivery_method}</dd>
            {order.delivery_address && <><dt>Address</dt><dd>{order.delivery_address}</dd></>}
            {order.pickup_location  && <><dt>Pickup at</dt><dd>{order.pickup_location}</dd></>}
            {order.assigned_driver  && <><dt>Driver</dt><dd>{order.assigned_driver}</dd></>}
            <dt>Placed</dt>
            <dd>{fmtDate(order.created_at)}</dd>
            {order.delivered_at && <><dt>Delivered</dt><dd>{fmtDate(order.delivered_at)}</dd></>}
          </dl>
        </div>

        {payment && (
          <div className="order-detail-block">
            <h4 className="order-detail-block-title">Payment</h4>
            <dl className="order-detail-dl">
              <dt>Card</dt>
              <dd>•••• {payment.card_num?.slice(-4)}</dd>
              <dt>Status</dt>
              <dd><span className={`payment-status-badge ${payment.status}`}>{payment.status}</span></dd>
              <dt>Charged</dt>
              <dd>${payment.price_total?.toFixed(2)}</dd>
              <dt>Updated</dt>
              <dd>{fmtDate(payment.updated_at)}</dd>
            </dl>
          </div>
        )}
      </div>

      {/* ── Admin: advance status ── */}
      {nextStatuses && nextStatuses.length > 0 && (
        <>
          <div className="order-detail-divider" />
          <div className="order-detail-block">
            <h4 className="order-detail-block-title">Advance Status</h4>
            <div className="status-actions">
              {nextStatuses.map((s) => (
                <button
                  key={s}
                  className={`btn btn-sm ${s === "cancelled" ? "btn-danger" : "btn-outline"}`}
                  disabled={statusBusy}
                  onClick={() => onStatusChange(s)}
                >
                  {statusBusy ? "…" : `→ ${s}`}
                </button>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
