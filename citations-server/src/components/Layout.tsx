import { useState, type FormEvent } from "react";
import { Outlet, useNavigate, useSearchParams, Link } from "react-router-dom";

export function Layout() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [query, setQuery] = useState(searchParams.get("q") ?? "");

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    const trimmed = query.trim();
    if (trimmed) {
      navigate(`/search?q=${encodeURIComponent(trimmed)}`);
    }
  }

  return (
    <div className="app">
      <header className="site-header">
        <Link to="/" className="site-title">HMLV Survey</Link>
        <nav className="header-nav">
          <Link to="/dashboard" className="header-link">Dashboard</Link>
          <Link to="/technology" className="header-link">Technologies</Link>
          <Link to="/country" className="header-link">Countries</Link>
          <Link to="/year" className="header-link">Years</Link>
        </nav>
        <form className="search-form" onSubmit={handleSubmit}>
          <input
            type="search"
            className="search-input"
            placeholder="Search papers by title, technology, method, country…"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          <button type="submit" className="search-btn">Search</button>
        </form>
      </header>
      <Outlet />
    </div>
  );
}
