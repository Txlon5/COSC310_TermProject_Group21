import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { updateSelf, deleteSelf, getMyCards, addCard, updateCard, deleteCard } from "../api";
import { useAuth } from "../useAuth";

const EMPTY_CARD = { card_num: "", card_cvc: "", card_exp: "", holder_name: "", holder_address: "" };

function initials(name) {
  return name
    .split(" ")
    .map((w) => w[0])
    .slice(0, 2)
    .join("")
    .toUpperCase();
}

export default function ProfilePage() {
  const { user, setUser, logout } = useAuth();
  const navigate = useNavigate();

  // Profile state
  const [profileForm, setProfileForm] = useState({ name: user.name, email: user.email, password: "" });
  const [profileError, setProfileError] = useState("");
  const [profileSuccess, setProfileSuccess] = useState("");
  const [profileLoading, setProfileLoading] = useState(false);
  const [editingProfile, setEditingProfile] = useState(false);

  // Cards state
  const [cards, setCards] = useState([]);
  const [cardsLoading, setCardsLoading] = useState(true);
  const [cardError, setCardError] = useState("");
  const [cardSuccess, setCardSuccess] = useState("");
  const [cardForm, setCardForm] = useState(EMPTY_CARD);
  const [editCardId, setEditCardId] = useState(null);
  const [showCardForm, setShowCardForm] = useState(false);
  const [cardSaving, setCardSaving] = useState(false);

  useEffect(() => {
    getMyCards()
      .then(setCards)
      .catch((err) => setCardError(err.message))
      .finally(() => setCardsLoading(false));
  }, []);

  // ── Profile handlers ───────────────────────────────────
  const setP = (field) => (e) =>
    setProfileForm((f) => ({ ...f, [field]: e.target.value }));

  const handleProfileSave = async (e) => {
    e.preventDefault();
    setProfileError(""); setProfileSuccess(""); setProfileLoading(true);
    try {
      const updated = await updateSelf({ ...profileForm, password: profileForm.password.trim() || null });
      setUser(updated);
      setProfileSuccess("Profile updated.");
      setEditingProfile(false);
    } catch (err) {
      setProfileError(err.message);
    } finally {
      setProfileLoading(false);
    }
  };

  const handleDeleteAccount = async () => {
    if (!window.confirm("Permanently delete your account? This cannot be undone.")) return;
    try {
      await deleteSelf();
      logout();
      navigate("/login");
    } catch (err) {
      setProfileError(err.message);
    }
  };

  // ── Card handlers ──────────────────────────────────────
  const setC = (field) => (e) => setCardForm((f) => ({ ...f, [field]: e.target.value }));

  const openAddCard = () => {
    setEditCardId(null); setCardForm(EMPTY_CARD);
    setCardError(""); setCardSuccess("");
    setShowCardForm(true);
  };
  const openEditCard = (card) => {
    setEditCardId(card.id);
    setCardForm({
      card_num: card.card_num, card_cvc: card.card_cvc,
      card_exp: card.card_exp, holder_name: card.holder_name,
      holder_address: card.holder_address,
    });
    setCardError(""); setCardSuccess("");
    setShowCardForm(true);
  };
  const closeCardForm = () => { setShowCardForm(false); setEditCardId(null); setCardForm(EMPTY_CARD); };

  const handleCardSave = async (e) => {
    e.preventDefault();
    setCardError(""); setCardSuccess(""); setCardSaving(true);
    try {
      if (editCardId) {
        const updated = await updateCard(editCardId, cardForm);
        setCards((c) => c.map((x) => (x.id === editCardId ? updated : x)));
        setCardSuccess("Card updated.");
      } else {
        const added = await addCard(cardForm);
        setCards((c) => [...c, added]);
        setCardSuccess("Card added.");
      }
      closeCardForm();
    } catch (err) {
      setCardError(err.message);
    } finally {
      setCardSaving(false);
    }
  };

  const handleDeleteCard = async (id) => {
    if (!window.confirm("Remove this card?")) return;
    try {
      await deleteCard(id);
      setCards((c) => c.filter((x) => x.id !== id));
    } catch (err) {
      setCardError(err.message);
    }
  };

  return (
    <div className="page-container profile-page">

      {/* ── Header ── */}
      <div className="profile-header">
        <div className="profile-avatar">{initials(user.name)}</div>
        <div className="profile-header-info">
          <h2>{user.name}</h2>
          <span className="profile-email">{user.email}</span>
          <span className={`role-pill ${user.role}`}>{user.role}</span>
        </div>
      </div>

      <div className="profile-grid">

        {/* ── Account details ── */}
        <section className="card profile-section">
          <div className="profile-section-header">
            <h3>Account Details</h3>
            {!editingProfile && (
              <button className="btn btn-sm btn-outline" onClick={() => setEditingProfile(true)}>
                Edit
              </button>
            )}
          </div>

          {profileError   && <div className="alert error">{profileError}</div>}
          {profileSuccess && <div className="alert success">{profileSuccess}</div>}

          {editingProfile ? (
            <form onSubmit={handleProfileSave}>
              <div className="form-group">
                <label>Name</label>
                <input type="text" value={profileForm.name} onChange={setP("name")} required />
              </div>
              <div className="form-group">
                <label>Email</label>
                <input type="email" value={profileForm.email} onChange={setP("email")} required />
              </div>
              <div className="form-group">
                <label>New Password</label>
                <input
                  type="password"
                  value={profileForm.password}
                  onChange={setP("password")}
                  placeholder="Leave blank to keep current"
                />
              </div>
              <div className="form-actions">
                <button className="btn btn-primary" disabled={profileLoading}>
                  {profileLoading ? "Saving…" : "Save Changes"}
                </button>
                <button type="button" className="btn btn-outline" onClick={() => setEditingProfile(false)}>
                  Cancel
                </button>
              </div>
            </form>
          ) : (
            <dl className="detail-list profile-detail-list">
              <dt>Name</dt>   <dd>{user.name}</dd>
              <dt>Email</dt>  <dd>{user.email}</dd>
              <dt>Role</dt>   <dd><span className={`role-pill ${user.role}`}>{user.role}</span></dd>
            </dl>
          )}

          <div className="profile-danger-zone">
            <button className="btn btn-sm btn-danger" onClick={handleDeleteAccount}>
              Delete Account
            </button>
            <span className="danger-hint">This action is permanent and cannot be undone.</span>
          </div>
        </section>

        {/* ── Payment Cards ── */}
        <section className="card profile-section">
          <div className="profile-section-header">
            <h3>Payment Cards</h3>
            <button className="btn btn-sm btn-primary" onClick={openAddCard}>+ Add Card</button>
          </div>

          {cardError   && <div className="alert error">{cardError}</div>}
          {cardSuccess && <div className="alert success">{cardSuccess}</div>}

          {showCardForm && (
            <form className="card-form-inline" onSubmit={handleCardSave}>
              <div className="form-group">
                <label>Card Number</label>
                <input
                  type="text" value={cardForm.card_num} onChange={setC("card_num")}
                  placeholder="1234 5678 9012 3456" required maxLength={19}
                />
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label>Expiry (YYYY-MM)</label>
                  <input
                    type="text" value={cardForm.card_exp} onChange={setC("card_exp")}
                    placeholder="2026-09" required maxLength={7}
                    pattern="\d{4}-(0[1-9]|1[0-2])" title="Format: YYYY-MM"
                  />
                </div>
                <div className="form-group">
                  <label>CVC</label>
                  <input
                    type="text" value={cardForm.card_cvc} onChange={setC("card_cvc")}
                    placeholder="123" required maxLength={4}
                  />
                </div>
              </div>
              <div className="form-group">
                <label>Cardholder Name</label>
                <input
                  type="text" value={cardForm.holder_name} onChange={setC("holder_name")}
                  placeholder="Jane Doe" required
                />
              </div>
              <div className="form-group">
                <label>Billing Address</label>
                <input
                  type="text" value={cardForm.holder_address} onChange={setC("holder_address")}
                  placeholder="123 Main St, City" required
                />
              </div>
              <div className="form-actions">
                <button className="btn btn-primary" disabled={cardSaving}>
                  {cardSaving ? "Saving…" : editCardId ? "Update Card" : "Add Card"}
                </button>
                <button type="button" className="btn btn-outline" onClick={closeCardForm}>Cancel</button>
              </div>
            </form>
          )}

          {cardsLoading ? (
            <div className="loading" style={{ padding: "1rem 0" }}>Loading cards…</div>
          ) : cards.length === 0 && !showCardForm ? (
            <p className="empty-state">No cards saved yet.</p>
          ) : (
            <div className="saved-cards">
              {cards.map((card) => (
                <div key={card.id} className="saved-card">
                  <div className="saved-card-chip">
                    <div className="chip-icon" />
                    <span className="saved-card-network">CARD</span>
                  </div>
                  <span className="saved-card-number">•••• •••• •••• {card.card_num.slice(-4)}</span>
                  <div className="saved-card-meta">
                    <span className="saved-card-name">{card.holder_name}</span>
                    <span className="saved-card-exp">{card.card_exp}</span>
                  </div>
                  <div className="saved-card-actions">
                    <button className="btn btn-sm btn-outline" onClick={() => openEditCard(card)}>Edit</button>
                    <button className="btn btn-sm btn-danger" onClick={() => handleDeleteCard(card.id)}>Remove</button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>

      </div>
    </div>
  );
}
