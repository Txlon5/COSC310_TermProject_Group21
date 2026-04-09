import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { getRestaurants } from "../api";

export default function RestaurantsPage() {
  const [restaurants, setRestaurants] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");
  const [tag, setTag] = useState("");
  const [openOnly, setOpenOnly] = useState(false);

  const fetchRestaurants = async ({ openOnlyVal = openOnly } = {}) => {
    setLoading(true);
    setError("");
    try {
      const params = {};
      if (search) params.q = search;
      if (tag) params.tag = tag;
      if (openOnlyVal) params.isOpen = true;
      const data = await getRestaurants(params);
      setRestaurants(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchRestaurants(); }, []);

  const handleSearch = (e) => { e.preventDefault(); fetchRestaurants(); };

  const handleOpenToggle = (e) => {
    const val = e.target.checked;
    setOpenOnly(val);
    fetchRestaurants({ openOnlyVal: val });
  };

  return (
    <div>
      {/* ── Hero search ── */}
      <div className="restaurants-hero">
        <h1 className="restaurants-hero-title">What are you hungry for?</h1>
        <form className="restaurants-search-form" onSubmit={handleSearch}>
          <div className="restaurants-search-row">
            <div className="restaurants-search-field">
              <label className="restaurants-search-label">Search</label>
              <input
                type="text"
                className="restaurants-search-input"
                placeholder="Restaurant name…"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </div>
            <div className="restaurants-search-field">
              <label className="restaurants-search-label">Tag</label>
              <input
                type="text"
                className="restaurants-search-input"
                placeholder="pizza, sushi…"
                value={tag}
                onChange={(e) => setTag(e.target.value)}
              />
            </div>
            <div className="restaurants-search-check">
              <label className={`restaurants-open-toggle ${openOnly ? "active" : ""}`}>
                <input
                  type="checkbox"
                  checked={openOnly}
                  onChange={handleOpenToggle}
                />
                <span className="restaurants-open-toggle-dot" />
                Open now
              </label>
            </div>
            <button className="btn btn-primary restaurants-search-btn" type="submit">Search</button>
          </div>
        </form>
      </div>

      {/* ── Results ── */}
      <div className="restaurants-divider" />
      <div className="page-container" style={{ paddingTop: "1.5rem" }}>
        {error && <div className="alert error">{error}</div>}
        {loading ? (
          <div className="loading">Loading restaurants…</div>
        ) : restaurants.length === 0 ? (
          <p className="empty-state">No restaurants found.</p>
        ) : (
          <>
            <p className="restaurants-count">{restaurants.length} restaurant{restaurants.length !== 1 ? "s" : ""}</p>
            <div className="card-grid">
              {restaurants.map((r) => (
                <Link key={r.restaurant_id} to={`/restaurants/${r.restaurant_id}`} className="restaurant-card">
                  <div className="restaurant-card-banner">
                    <span className="restaurant-card-banner-name">{r.restaurant_name}</span>
                    <span className={`status-badge ${r.isOpen ? "open" : "closed"}`}>
                      {r.isOpen ? "Open" : "Closed"}
                    </span>
                  </div>
                  <div className="restaurant-card-inner">
                    {r.tags && r.tags.length > 0 && (
                      <div className="tags">
                        {r.tags.map((t) => <span key={t} className="tag">{t}</span>)}
                      </div>
                    )}
                    {r.opening_time && r.closing_time && (
                      <p className="restaurant-hours">{r.opening_time} – {r.closing_time}</p>
                    )}
                    {r.menuItems && r.menuItems.length > 0 && (
                      <p className="item-count">{r.menuItems.length} item{r.menuItems.length !== 1 ? "s" : ""}</p>
                    )}
                  </div>
                </Link>
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
