import { useState, useEffect, useRef } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faBell, faCartShopping, faBox, faCircleCheck, faRecordVinyl } from "@fortawesome/free-solid-svg-icons";
import { useAuth } from "../useAuth";
import { useCart } from "../CartContext";
import { getNotifications } from "../api";

export default function Navbar() {
  const { user, logout } = useAuth();
  const { cart } = useCart();
  const navigate = useNavigate();
  const location = useLocation();

  const [notifications, setNotifications] = useState([]);
  const [notifOpen, setNotifOpen] = useState(false);
  const notifRef = useRef(null);

  const cartCount = cart.items.reduce((s, i) => s + i.quantity, 0);

  // Load notifications whenever the user changes
  useEffect(() => {
    if (!user) return;
    getNotifications(user.id)
      .then(setNotifications)
      .catch(() => {});
  }, [user?.id]);

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClick(e) {
      if (notifRef.current && !notifRef.current.contains(e.target)) {
        setNotifOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, []);

  // Close dropdown on route change
  useEffect(() => {
    setNotifOpen(false);
  }, [location.pathname]);

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  const active = (path) =>
    location.pathname === path ? "nav-link active" : "nav-link";

  if (!user) {
    return (
      <nav className="navbar">
        <Link to="/" className="navbar-brand">
        <FontAwesomeIcon icon={faRecordVinyl} /> Platter
      </Link>
        <div className="navbar-links">
          <Link to="/" className={active("/")}>Restaurants</Link>
        </div>
        <div className="navbar-right">
          <Link to="/login" className="btn btn-sm btn-outline">Login</Link>
          <Link to="/register" className="btn btn-sm btn-primary">Sign Up</Link>
        </div>
      </nav>
    );
  }

  const sorted = [...notifications].sort(
    (a, b) => new Date(b.timestamp) - new Date(a.timestamp)
  );

  const TYPE_ICONS = {
    order_created: { icon: faCartShopping, color: "#e85c2d" },
    status_update: { icon: faBox,          color: "#7c3aed" },
    delivered:     { icon: faCircleCheck,  color: "#15803d" },
  };

  return (
    <nav className="navbar">
      <Link to="/" className="navbar-brand">
        <FontAwesomeIcon icon={faRecordVinyl} /> Platter
      </Link>

      <div className="navbar-links">
        <Link to="/" className={active("/")}>Restaurants</Link>
        <Link to="/orders" className={active("/orders")}>Orders</Link>
        {user.role === "admin" && (
          <Link to="/admin" className={active("/admin")} style={{ color: "#7c3aed" }}>Admin</Link>
        )}
      </div>

      <div className="navbar-right">
        {cartCount > 0 && (
          <Link to="/cart" className="cart-badge">
            <FontAwesomeIcon icon={faCartShopping} /> {cartCount}
          </Link>
        )}

        {/* Notification bell */}
        <div className="notif-dropdown-wrap" ref={notifRef}>
          <button
            className={`notif-bell ${notifOpen ? "open" : ""}`}
            onClick={() => setNotifOpen((o) => !o)}
            aria-label="Notifications"
          >
            <FontAwesomeIcon icon={faBell} />
            {notifications.length > 0 && (
              <span className="notif-count">{notifications.length > 99 ? "99+" : notifications.length}</span>
            )}
          </button>

          {notifOpen && (
            <div className="notif-dropdown">
              <div className="notif-dropdown-header">
                <span>Notifications</span>
                {notifications.length > 0 && (
                  <span className="notif-dropdown-count">{notifications.length}</span>
                )}
              </div>
              <div className="notif-dropdown-body">
                {sorted.length === 0 ? (
                  <p className="notif-empty">No notifications.</p>
                ) : (
                  sorted.map((n, i) => (
                    <div key={i} className="notif-dropdown-item">
                      <span className="notif-icon" style={{ color: (TYPE_ICONS[n.type] || {}).color || "#888" }}>
                        <FontAwesomeIcon icon={(TYPE_ICONS[n.type] || {}).icon || faBell} />
                      </span>
                      <div className="notif-body">
                        <strong className="notif-title">{n.title}</strong>
                        {n.order_id && (
                          <span className="notif-orderid">#{n.order_id}</span>
                        )}
                        <p className="notif-message">{n.message}</p>
                        <span className="notif-time">
                          {new Date(n.timestamp).toLocaleString(undefined, {
                            month: "short", day: "numeric",
                            hour: "2-digit", minute: "2-digit",
                          })}
                        </span>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}
        </div>

        <div className="navbar-user">
          <Link to="/profile" className="nav-link">{user.name}</Link>
          <button className="btn btn-sm btn-outline" onClick={handleLogout}>Logout</button>
        </div>
      </div>
    </nav>
  );
}
