import { BrowserRouter, Routes, Route } from "react-router-dom";
import papersData from "./data/papers.json";
import relevantPapersData from "./data/relevant-papers.json";
import type { Paper, RelevantPaper } from "./types";
import { Layout } from "./components/Layout";
import { LevelSelect } from "./pages/LevelSelect";
import { DSSFocusSelect } from "./pages/DSSFocusSelect";
import { SubCategorySelect } from "./pages/SubCategorySelect";
import { PaperList } from "./pages/PaperList";
import { PaperDetail } from "./pages/PaperDetail";
import { SearchResults } from "./pages/SearchResults";
import { Dashboard } from "./pages/Dashboard";
import { RelevantPapers } from "./pages/RelevantPapers";
import {
  TechnologyIndex, TechnologyPapers,
  CountryIndex, CountryPapers,
  YearIndex, YearPapers,
} from "./pages/BrowseBy";

const papers: Paper[] = papersData as Paper[];
const relevantPapers: RelevantPaper[] = relevantPapersData as RelevantPaper[];

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<LevelSelect papers={papers} />} />
          <Route path="/search" element={<SearchResults papers={papers} />} />
          <Route path="/possibly-relevant" element={<RelevantPapers papers={relevantPapers} />} />
          <Route path="/dashboard" element={<Dashboard papers={papers} />} />
          <Route path="/technology" element={<TechnologyIndex papers={papers} />} />
          <Route path="/technology/:tech" element={<TechnologyPapers papers={papers} />} />
          <Route path="/country" element={<CountryIndex papers={papers} />} />
          <Route path="/country/:country" element={<CountryPapers papers={papers} />} />
          <Route path="/year" element={<YearIndex papers={papers} />} />
          <Route path="/year/:year" element={<YearPapers papers={papers} />} />
          <Route path="/level/:level" element={<DSSFocusSelect papers={papers} />} />
          <Route path="/level/:level/focus/:focus" element={<SubCategorySelect />} />
          <Route path="/level/:level/focus/:focus/papers" element={<PaperList papers={papers} />} />

          <Route path="/paper/:id" element={<PaperDetail papers={papers} />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
