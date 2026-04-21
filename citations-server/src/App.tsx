import { BrowserRouter, Routes, Route } from "react-router-dom";
import papersData from "./data/papers.json";
import type { Paper } from "./types";
import { Layout } from "./components/Layout";
import { LevelSelect } from "./pages/LevelSelect";
import { DSSFocusSelect } from "./pages/DSSFocusSelect";
import { SubCategorySelect, VariantPaperList } from "./pages/SubCategorySelect";
import { PaperList } from "./pages/PaperList";
import { PaperDetail } from "./pages/PaperDetail";
import { SearchResults } from "./pages/SearchResults";
import { Dashboard } from "./pages/Dashboard";
import {
  TechnologyIndex, TechnologyPapers,
  CountryIndex, CountryPapers,
  YearIndex, YearPapers,
} from "./pages/BrowseBy";

const papers: Paper[] = papersData as Paper[];

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<LevelSelect papers={papers} />} />
          <Route path="/search" element={<SearchResults papers={papers} />} />
          <Route path="/dashboard" element={<Dashboard papers={papers} />} />
          <Route path="/technology" element={<TechnologyIndex papers={papers} />} />
          <Route path="/technology/:tech" element={<TechnologyPapers papers={papers} />} />
          <Route path="/country" element={<CountryIndex papers={papers} />} />
          <Route path="/country/:country" element={<CountryPapers papers={papers} />} />
          <Route path="/year" element={<YearIndex papers={papers} />} />
          <Route path="/year/:year" element={<YearPapers papers={papers} />} />
          <Route path="/level/:level" element={<DSSFocusSelect papers={papers} />} />
          <Route path="/level/:level/focus/:focus" element={<SubCategorySelect papers={papers} />} />
          <Route path="/level/:level/focus/:focus/papers" element={<PaperList papers={papers} />} />
          <Route path="/level/:level/focus/:focus/variant/:variant" element={<VariantPaperList papers={papers} />} />
          <Route path="/paper/:id" element={<PaperDetail papers={papers} />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
