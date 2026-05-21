export interface Paper {
  id: number;
  title: string;
  year: number;
  doi: string;
  bibtexKey: string;
  manufacturingLevel: string;
  dssFocus: string;
  dssFocusGrouped?: string;
  jobShopVariation: string | null;
  technologies: string[];
  methods: string[];
  evaluationSetting: string;
  dataSource: string[];
  country: string;
  industry: string;
  metrics: string;
  snowball: boolean;
}

export interface RelevantPaper {
  id: number;
  keyId: string;
  title: string;
  doi: string;
  relevanceScore: string;
  reasoning: string;
  methods: string[];
  technologies: string[];
  automatedManufacturingLevel: string;
  negativesFound: string;
  dssFocus: string;
  year: number;
}
