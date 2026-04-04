import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { getRestaurantById, getRestaurantMenu } from "../api";
import { useCart } from "../CartContext";
import { useAuth } from "../useAuth";

export default function RestaurantDetailPage() {
  const { id } = useParams();
  const { user } = useAuth();
  const { addItem, cart } = useCart();
  const [restaurant, setRestaurant] = useState(null);
  const [menu, setMenu] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [added, setAdded] = useState(null);

  useEffect(() => {
    Promise.all([getRestaurantById(id), getRestaurantMenu(id)])
      .then(([r, m]) => {
        setRestaurant(r);
        setMenu(m);
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [id]);

  const handleAdd = (item) => {
    addItem(id, restaurant.restaurant_name, item);
    setAdded(item.menuItemId);
    setTimeout(() => setAdded(null), 1200);
  };

  const cartQty = (itemId) => {
    if (cart.restaurantId !== id) return 0;
    return cart.items.find((i) => i.id === itemId)?.quantity || 0;
  };

  if (loading) return <div className="loading">Loading…</div>;
  if (error) return <div className="page-container"><div className="alert error">{error}</div></div>;
  if (!restaurant) return null;

  const PALETTE = ["#c2410c","#0e7490","#6d28d9","#047857","#b45309","#be185d","#1d4ed8","#065f46"];
  const bannerColor = PALETTE[id.split("").reduce((acc, c) => acc + c.charCodeAt(0), 0) % PALETTE.length];

  const categories = [...new Set(menu.map((i) => i.category))];

  return (
    <div className="page-container">
    <div className="restaurant-detail-wrap">
      <div className="restaurant-header" style={{ "--card-bg": bannerColor }}>
        <div className="restaurant-header-info">
          <h2>{restaurant.restaurant_name}</h2>
          <div className="tags">
            {restaurant.tags.map((t) => <span key={t} className="tag">{t}</span>)}
          </div>
          <span className={`status-badge large ${restaurant.isOpen ? "open" : "closed"}`}>
            {restaurant.isOpen ? "Open" : "Closed"}
          </span>
        </div>
      </div>

      {cart.items.length > 0 && (
        <div className="cart-banner">
          <span>{cart.items.reduce((s, i) => s + i.quantity, 0)} item(s) in cart</span>
          <Link to="/cart" className="btn btn-primary btn-sm">View Cart</Link>
        </div>
      )}

      {menu.length === 0 ? (
        <p className="empty-state">No menu items available.</p>
      ) : (
        categories.map((cat) => (
          <div key={cat} className="menu-section">
            <h3 className="menu-category">{cat}</h3>
            <div className="menu-grid">
              {menu.filter((i) => i.category === cat).map((item) => {
                const qty = cartQty(item.menuItemId);
                return (
                  <div key={item.menuItemId} className="menu-item-card">
                    <div className="menu-item-info">
                      <span className="menu-item-name">{item.name}</span>
                    </div>
                    <div className="menu-item-footer">
                      <span className="menu-item-price">${item.price.toFixed(2)}</span>
                      {user ? (
                        <button
                          className={`btn btn-sm ${added === item.menuItemId ? "btn-success" : "btn-primary"}`}
                          onClick={() => handleAdd(item)}
                          disabled={!restaurant.isOpen}
                        >
                          {added === item.menuItemId ? "Added!" : qty > 0 ? `Add (${qty})` : "Add"}
                        </button>
                      ) : (
                        <Link to="/login" className="btn btn-sm btn-outline">Login to add</Link>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        ))
      )}
    </div>
    </div>
  );
}
