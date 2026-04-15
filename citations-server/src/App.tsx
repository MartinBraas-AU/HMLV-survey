import { BrowserRouter, Routes, Route } from "react-router-dom";
import papersData from "./data/papers.json";
import type { Paper } from "./types";
import { LevelSelect } from "./pages/LevelSelect";
import { DSSFocusSelect } from "./pages/DSSFocusSelect";
import { SubCategorySelect, VariantPaperList } from "./pages/SubCategorySelect";
import { PaperList } from "./pages/PaperList";
import { PaperDetail } from "./pages/PaperDetail";

const papers: Paper[] = papersData as Paper[];

const basename = import.meta.env.BASE_URL.replace(/\/$/, "");

function App() {
  return (
    <BrowserRouter basename={basename}>
      <div className="app">
        <Routes>
          <Route path="/" element={<LevelSelect papers={papers} />} />
          <Route path="/level/:level" element={<DSSFocusSelect papers={papers} />} />
          <Route path="/level/:level/focus/:focus" element={<SubCategorySelect papers={papers} />} />
          <Route path="/level/:level/focus/:focus/papers" element={<PaperList papers={papers} />} />
          <Route path="/level/:level/focus/:focus/variant/:variant" element={<VariantPaperList papers={papers} />} />
          <Route path="/paper/:id" element={<PaperDetail papers={papers} />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;
