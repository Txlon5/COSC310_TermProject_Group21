import { useState, useEffect } from "react";
import { getNotifications } from "../api";
import { useAuth } from "../useAuth";

const TYPE_ICONS = {
  order_created: "🛒",
  status_update: "📦",
  delivered: "✅",
};

export default function NotificationsPage() {
  const { user } = useAuth();
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    getNotifications(user.id)
      .then(setNotifications)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [user.id]);

  if (loading) return <div className="loading">Loading notifications…</div>;

  return (
    <div className="page-container">
      <h2>Notifications</h2>
      {error && <div className="alert error">{error}</div>}
      {notifications.length === 0 ? (
        <p className="empty-state">No notifications.</p>
      ) : (
        <div className="notification-list">
          {notifications
            .slice()
            .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
            .map((n, i) => (
              <div key={i} className="notification-item">
                <span className="notif-icon">{TYPE_ICONS[n.type] || "🔔"}</span>
                <div className="notif-body">
                  <strong className="notif-title">{n.title}</strong>
                  <p className="notif-message">{n.message}</p>
                  <span className="notif-time">
                    {new Date(n.timestamp).toLocaleString()}
                  </span>
                </div>
              </div>
            ))}
        </div>
      )}
    </div>
  );
}
