import { Link } from "react-router-dom";

interface CategoryCardProps {
  label: string;
  count: number;
  to: string;
}

export function CategoryCard({ label, count, to }: CategoryCardProps) {
  return (
    <Link to={to} className="category-card">
      <div className="category-card-label">{label}</div>
      <div className="category-card-count">{count} papers</div>
    </Link>
  );
}
