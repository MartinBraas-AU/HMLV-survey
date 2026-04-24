import { useParams, Navigate } from "react-router-dom";

export function SubCategorySelect() {
  const { level, focus } = useParams<{ level: string; focus: string }>();

  return (
    <Navigate
      to={`/level/${encodeURIComponent(level!)}/focus/${encodeURIComponent(focus!)}/papers`}
      replace
    />
  );
}
