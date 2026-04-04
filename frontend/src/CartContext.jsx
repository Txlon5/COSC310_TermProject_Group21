import { createContext, useContext, useState, useEffect } from "react";

const CartContext = createContext(null);

const STORAGE_KEY = "cart";

function loadCart() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : { restaurantId: null, restaurantName: "", items: [] };
  } catch {
    return { restaurantId: null, restaurantName: "", items: [] };
  }
}

function saveCart(cart) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(cart));
}

export function CartProvider({ children }) {
  const [cart, setCart] = useState(loadCart);

  useEffect(() => {
    saveCart(cart);
  }, [cart]);

  const addItem = (restaurantId, restaurantName, item) => {
    setCart((prev) => {
      if (prev.restaurantId && prev.restaurantId !== restaurantId) {
        if (!window.confirm("Your cart has items from another restaurant. Clear cart and add new item?")) {
          return prev;
        }
        return { restaurantId, restaurantName, items: [{ ...item, quantity: 1 }] };
      }
      const existing = prev.items.find((i) => i.menuItemId === item.menuItemId);
      if (existing) {
        return {
          ...prev,
          restaurantId,
          restaurantName,
          items: prev.items.map((i) =>
            i.menuItemId === item.menuItemId ? { ...i, quantity: i.quantity + 1 } : i
          ),
        };
      }
      return {
        ...prev,
        restaurantId,
        restaurantName,
        items: [...prev.items, { ...item, quantity: 1 }],
      };
    });
  };

  const removeItem = (menuItemId) => {
    setCart((prev) => {
      const updated = prev.items
        .map((i) => (i.menuItemId === menuItemId ? { ...i, quantity: i.quantity - 1 } : i))
        .filter((i) => i.quantity > 0);
      return { ...prev, items: updated };
    });
  };

  const clearCart = () => {
    const empty = { restaurantId: null, restaurantName: "", items: [] };
    setCart(empty);
  };

  const total = cart.items.reduce((sum, i) => sum + i.price * i.quantity, 0);

  return (
    <CartContext.Provider value={{ cart, addItem, removeItem, clearCart, total }}>
      {children}
    </CartContext.Provider>
  );
}

export function useCart() {
  return useContext(CartContext);
}
