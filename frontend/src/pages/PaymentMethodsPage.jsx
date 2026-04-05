import { useState, useEffect } from "react";
import { getMyCards, addCard, updateCard, deleteCard } from "../api";

const EMPTY_FORM = { card_num: "", card_cvc: "", card_exp: "", holder_name: "", holder_address: "" };

export default function PaymentMethodsPage() {
  const [cards, setCards] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [editId, setEditId] = useState(null);
  const [form, setForm] = useState(EMPTY_FORM);
  const [saving, setSaving] = useState(false);

  const load = () => {
    setLoading(true);
    getMyCards()
      .then(setCards)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  };

  useEffect(load, []);

  const set = (field) => (e) => setForm((f) => ({ ...f, [field]: e.target.value }));

  const openAdd = () => { setEditId(null); setForm(EMPTY_FORM); setShowForm(true); };
  const openEdit = (card) => {
    setEditId(card.id);
    setForm({ card_num: card.card_num, card_cvc: card.card_cvc, card_exp: card.card_exp, holder_name: card.holder_name, holder_address: card.holder_address });
    setShowForm(true);
  };
  const closeForm = () => { setShowForm(false); setEditId(null); setForm(EMPTY_FORM); };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(""); setSuccess(""); setSaving(true);
    try {
      if (editId) {
        const updated = await updateCard(editId, form);
        setCards((c) => c.map((x) => (x.id === editId ? updated : x)));
        setSuccess("Card updated.");
      } else {
        const added = await addCard(form);
        setCards((c) => [...c, added]);
        setSuccess("Card added.");
      }
      closeForm();
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Remove this card?")) return;
    try {
      await deleteCard(id);
      setCards((c) => c.filter((x) => x.id !== id));
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="page-container">
      <div className="page-header">
        <h2>Payment Methods</h2>
        <button className="btn btn-primary" onClick={openAdd}>+ Add Card</button>
      </div>

      {error && <div className="alert error">{error}</div>}
      {success && <div className="alert success">{success}</div>}

      {showForm && (
        <div className="card" style={{ maxWidth: 480, marginBottom: "1.5rem" }}>
          <h3>{editId ? "Edit Card" : "Add Card"}</h3>
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label>Card Number</label>
              <input type="text" value={form.card_num} onChange={set("card_num")} placeholder="1234 5678 9012 3456" required maxLength={19} />
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>Expiry (YYYY-MM)</label>
                <input type="text" value={form.card_exp} onChange={set("card_exp")} placeholder="2026-09" required maxLength={7} pattern="\d{4}-(0[1-9]|1[0-2])" title="Format: YYYY-MM (e.g. 2026-09)" />
              </div>
              <div className="form-group">
                <label>CVC</label>
                <input type="text" value={form.card_cvc} onChange={set("card_cvc")} placeholder="123" required maxLength={4} />
              </div>
            </div>
            <div className="form-group">
              <label>Cardholder Name</label>
              <input type="text" value={form.holder_name} onChange={set("holder_name")} placeholder="Jane Doe" required />
            </div>
            <div className="form-group">
              <label>Billing Address</label>
              <input type="text" value={form.holder_address} onChange={set("holder_address")} placeholder="123 Main St, City" required />
            </div>
            <div className="form-actions">
              <button className="btn btn-primary" disabled={saving}>{saving ? "Saving…" : "Save"}</button>
              <button type="button" className="btn btn-outline" onClick={closeForm}>Cancel</button>
            </div>
          </form>
        </div>
      )}

      {loading ? (
        <div className="loading">Loading cards…</div>
      ) : cards.length === 0 ? (
        <p className="empty-state">No payment methods saved.</p>
      ) : (
        <div className="card-list">
          {cards.map((card) => (
            <div key={card.id} className="card payment-card">
              <div className="payment-card-info">
                <span className="card-number">•••• •••• •••• {card.card_num.slice(-4)}</span>
                <span className="card-holder">{card.holder_name}</span>
                <span className="card-exp">Exp: {card.card_exp}</span>
                <span className="card-address" style={{ fontSize: "0.78rem", color: "#aaa" }}>{card.holder_address}</span>
              </div>
              <div className="payment-card-actions">
                <button className="btn btn-sm btn-outline" onClick={() => openEdit(card)}>Edit</button>
                <button className="btn btn-sm btn-danger" onClick={() => handleDelete(card.id)}>Remove</button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
