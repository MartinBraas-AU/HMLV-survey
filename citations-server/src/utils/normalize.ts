import type { Paper } from "../types";

export function groupBy<T>(items: T[], key: (item: T) => string): Map<string, T[]> {
  const map = new Map<string, T[]>();
  for (const item of items) {
    const k = key(item);
    const existing = map.get(k);
    if (existing) {
      existing.push(item);
    } else {
      map.set(k, [item]);
    }
  }
  return map;
}

export function sortedEntries<T>(map: Map<string, T[]>): [string, T[]][] {
  return [...map.entries()].sort((a, b) => b[1].length - a[1].length);
}

export function papersByLevel(papers: Paper[]): Map<string, Paper[]> {
  return groupBy(papers, (p) => p.manufacturingLevel);
}

export function papersByDSSFocus(papers: Paper[]): Map<string, Paper[]> {
  return groupBy(papers, (p) => p.dssFocus);
}

export function papersByJobShopVariant(papers: Paper[]): Map<string, Paper[]> {
  const scheduling = papers.filter((p) => p.jobShopVariation);
  const noVariant = papers.filter((p) => !p.jobShopVariation);
  const map = groupBy(scheduling, (p) => p.jobShopVariation!);
  if (noVariant.length > 0) {
    map.set("Other Scheduling", noVariant);
  }
  return map;
}

const LEVEL_ORDER = ["L0", "L1", "L2", "L3", "L3/L4", "L4"];

export function sortLevels(levels: string[]): string[] {
  return levels.sort((a, b) => {
    const ai = LEVEL_ORDER.indexOf(a);
    const bi = LEVEL_ORDER.indexOf(b);
    return (ai === -1 ? 99 : ai) - (bi === -1 ? 99 : bi);
  });
}
