import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useCart } from "../CartContext";
import { useAuth } from "../useAuth";
import { createOrder, getMyCards, getRestaurantById } from "../api";

export default function CartPage() {
  const { cart, addItem, removeItem, clearCart, total } = useCart();
  const { user } = useAuth();
  const navigate = useNavigate();

  const [cards, setCards] = useState([]);
  const [selectedCard, setSelectedCard] = useState("");
  const [deliveryMethod, setDeliveryMethod] = useState("delivery");
  const [deliveryAddress, setDeliveryAddress] = useState("");
  const [pickupLocation, setPickupLocation] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [restaurantOpen, setRestaurantOpen] = useState(null);

  useEffect(() => {
    if (!cart.restaurantId) return;
    getRestaurantById(cart.restaurantId)
      .then((r) => setRestaurantOpen(r.isOpen))
      .catch(() => {});
  }, [cart.restaurantId]);

  useEffect(() => {
    getMyCards()
      .then((c) => {
        setCards(c);
        if (c.length > 0) setSelectedCard(c[0].id);
      })
      .catch(() => {});
  }, []);

  const handleCheckout = async () => {
    setError("");
    if (!selectedCard) {
      setError("Please add a payment method first.");
      return;
    }
    if (cart.items.length === 0) {
      setError("Your cart is empty.");
      return;
    }
    if (deliveryMethod === "delivery" && !deliveryAddress.trim()) {
      setError("Please enter a delivery address.");
      return;
    }
    if (deliveryMethod === "pickup" && !pickupLocation.trim()) {
      setError("Please enter a pickup location.");
      return;
    }

    setLoading(true);
    try {
      const payload = {
        user_id: user.id,
        card_id: selectedCard,
        restaurant_id: cart.restaurantId,
        items: cart.items.map((i) => ({
          menuItemId: i.menuItemId,
          name: i.name,
          price: i.price,
          quantity: i.quantity,
        })),
        delivery_method: deliveryMethod,
        delivery_address: deliveryMethod === "delivery" ? deliveryAddress : null,
        pickup_location: deliveryMethod === "pickup" ? pickupLocation : null,
      };
      const order = await createOrder(payload);
      clearCart();
      navigate(`/orders/${order.order_id}`);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (cart.items.length === 0) {
    return (
      <div className="page-container">
        <h2>Cart</h2>
        <p className="empty-state">Your cart is empty. <a href="/">Browse restaurants</a></p>
      </div>
    );
  }

  return (
    <div className="page-container">
      <h2>Cart — {cart.restaurantName}</h2>
      {restaurantOpen === false && (
        <div className="alert warning">
          This restaurant is currently closed and not accepting orders right now.
        </div>
      )}
      {error && <div className="alert error">{error}</div>}

      <div className="cart-layout">
        <div className="card">
          <h3>Items</h3>
          {cart.items.map((item) => (
            <div key={item.id} className="cart-item">
              <div className="cart-item-info">
                <span className="cart-item-name">{item.name}</span>
                <span className="cart-item-price">${(item.price * item.quantity).toFixed(2)}</span>
              </div>
              <div className="cart-item-controls">
                <button className="btn btn-sm btn-outline" onClick={() => removeItem(item.menuItemId)}>−</button>
                <span className="cart-qty">{item.quantity}</span>
                <button className="btn btn-sm btn-outline" onClick={() => addItem(cart.restaurantId, cart.restaurantName, item)}>+</button>
              </div>
            </div>
          ))}
          <div className="cart-total">
            <strong>Total: ${total.toFixed(2)}</strong>
          </div>
        </div>

        <div className="card">
          <h3>Checkout</h3>

          <div className="form-group">
            <label>Delivery Method</label>
            <select value={deliveryMethod} onChange={(e) => setDeliveryMethod(e.target.value)}>
              <option value="delivery">Delivery</option>
              <option value="pickup">Pickup</option>
            </select>
          </div>

          {deliveryMethod === "delivery" && (
            <div className="form-group">
              <label>Delivery Address</label>
              <input
                type="text"
                value={deliveryAddress}
                onChange={(e) => setDeliveryAddress(e.target.value)}
                placeholder="123 Main St, City, Province"
              />
            </div>
          )}

          {deliveryMethod === "pickup" && (
            <div className="form-group">
              <label>Pickup Location</label>
              <input
                type="text"
                value={pickupLocation}
                onChange={(e) => setPickupLocation(e.target.value)}
                placeholder="e.g. Front entrance"
              />
            </div>
          )}

          <div className="form-group">
            <label>Payment Card</label>
            {cards.length === 0 ? (
              <p className="hint">
                No cards saved. <a href="/profile">Add a card</a> first.
              </p>
            ) : (
              <select value={selectedCard} onChange={(e) => setSelectedCard(e.target.value)}>
                {cards.map((c) => (
                  <option key={c.id} value={c.id}>
                    •••• {c.card_num.slice(-4)} — {c.holder_name}
                  </option>
                ))}
              </select>
            )}
          </div>

          <button
            className="btn btn-primary w-full"
            onClick={handleCheckout}
            disabled={loading || cards.length === 0 || restaurantOpen === false}
          >
            {loading ? "Placing order…" : `Place Order — $${total.toFixed(2)}`}
          </button>
          <button className="btn btn-outline w-full mt-sm" onClick={clearCart}>
            Clear Cart
          </button>
        </div>
      </div>
    </div>
  );
}
