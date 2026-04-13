export interface Paper {
  id: number;
  title: string;
  year: number;
  doi: string;
  bibtexKey: string;
  manufacturingLevel: string;
  dssFocus: string;
  jobShopVariation: string | null;
  technologies: string[];
  methods: string[];
  evaluationSetting: string;
  dataSource: string;
  country: string;
  industry: string;
  metrics: string;
  snowball: boolean;
}
