/** Browser evidence contracts and pure rendering helpers by Jason Stys.
 * Functions: escapeText, readPreferences, query, timelineMarkup. Variables/types: settings,
 * fixed station/craft identifiers and API evidence. Definition lines: docs/CODE_INDEX.md.
 */
export const scenarios = [
  "nominal",
  "station-outage",
  "maintenance",
  "tight-energy",
  "urgent-insertion",
  "impossible-deadline",
  "greedy-trap",
  "unreachable-window",
] as const;
export const choices = {
  guard: [0, 1, 2],
  energy_cap: [12, 24, 40],
  station_budget: [24, 36, 60],
  policy: [0, 1],
} as const;
export interface Settings {
  scenario: string;
  guard: number;
  energy_cap: number;
  station_budget: number;
  policy: number;
}
export const defaults: Settings = {
  scenario: "nominal",
  guard: 1,
  energy_cap: 24,
  station_budget: 36,
  policy: 1,
};
export interface Candidate {
  id: string;
  request: string;
  station: string;
  spacecraft: string;
  start: number;
  end: number;
  energy: number;
  rate: number;
  selected: boolean;
  baseline: boolean;
  reasons: string[];
}
export interface RequestInfo {
  id: string;
  spacecraft: string;
  band: string;
  priority: number;
  units: number;
  release: number;
  deadline: number;
  selected: string | null;
  alternatives: string[];
}
export interface Plan {
  selected: string[];
  utility: number;
  energy: number;
  reserved: number;
  units: number;
  fulfilled: number;
  violations: string[];
  status?: string;
  visited_nodes?: number;
}
export interface Usage {
  name: string;
  used: number;
  budget: number;
}
export interface Evidence {
  id: string;
  scenario: string;
  settings: Settings;
  exact: Plan;
  greedy: Plan;
  delta: number;
  outage_comparisons: {
    station: string;
    outage: { start: number; end: number };
    exact: Plan;
    retained: string[];
    removed: string[];
    added: string[];
    utility_loss: number;
    fulfilled_delta: number;
    energy_delta: number;
    directly_blocked: { id: string; reasons: string[] }[];
    request_changes: { request: string; before: string | null; after: string | null }[];
  }[];
  candidates: Candidate[];
  requests: RequestInfo[];
  station_usage: Usage[];
  energy_usage: Usage[];
  case: { blackouts: { station: string; start: number; end: number }[] };
}

/** Escape every dynamic HTML/SVG text and attribute value; never interpret evidence as markup. */
export function escapeText(value: unknown): string {
  return String(value).replace(
    /[&<>"']/g,
    (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[char]!,
  );
}

/** Accept only a complete finite settings object; reject prototypes, unknown keys and coercion. */
export function readPreferences(raw: string | null): Settings | null {
  if (!raw || raw.length > 512) return null;
  try {
    const value: unknown = JSON.parse(raw);
    if (!value || typeof value !== "object" || Array.isArray(value)) return null;
    const obj = value as Record<string, unknown>;
    if (
      Object.keys(obj).length !== 5 ||
      !Object.hasOwn(obj, "scenario") ||
      !(scenarios as readonly unknown[]).includes(obj.scenario)
    )
      return null;
    for (const [key, allowed] of Object.entries(choices))
      if (!Object.hasOwn(obj, key) || !(allowed as readonly unknown[]).includes(obj[key]))
        return null;
    return obj as unknown as Settings;
  } catch {
    return null;
  }
}

/** Serialize a validated finite control set; no source paths or arbitrary service URLs. */
export function query(settings: Settings): string {
  return new URLSearchParams(
    Object.entries(settings).map(([key, value]) => [key, String(value)]),
  ).toString();
}

/** Draw a proportional half-open timeline using SVG attributes, not CSP-blocked inline styles. */
export function timelineMarkup(run: Evidence, baseline: boolean, craft: string): string {
  const plan = baseline ? run.greedy : run.exact;
  const selected = run.candidates.filter(
    (item) => plan.selected.includes(item.id) && (craft === "ALL" || item.spacecraft === craft),
  );
  const stations = ["ALPHA", "BRAVO", "CHARLIE"];
  const x = (tick: number) => 120 + tick * 6;
  const ticks = Array.from({ length: 7 }, (_, index) => {
    const tick = index * 20;
    return `<line class="grid-line" x1="${x(tick)}" x2="${x(tick)}" y1="25" y2="240"/><text class="tick-label" x="${x(tick)}" y="265" text-anchor="middle">${tick}</text>`;
  }).join("");
  const lanes = stations
    .map((station, index) => {
      const y = 50 + index * 70;
      const blocked = run.case.blackouts
        .filter((item) => item.station === station)
        .map(
          (item) =>
            `<rect class="blackout" x="${x(item.start)}" y="${y - 14}" width="${(item.end - item.start) * 6}" height="48"/><text class="blackout-label" x="${x(item.start) + 5}" y="${y + 14}">UNAVAILABLE</text>`,
        )
        .join("");
      const bars = selected
        .filter((item) => item.station === station)
        .map(
          (item) =>
            `<g class="craft-${escapeText(item.spacecraft.slice(-1).toLowerCase())}"><title>${escapeText(`${item.id} / ${item.request} / ${item.spacecraft}: ${item.start}–${item.end}; guard ${run.settings.guard} each side`)}</title><rect class="guard-bar" x="${x(item.start - run.settings.guard)}" y="${y - 8}" width="${(item.end - item.start + run.settings.guard * 2) * 6}" height="36" rx="3"/><rect class="contact-bar" x="${x(item.start)}" y="${y - 3}" width="${(item.end - item.start) * 6}" height="26" rx="2"/><text class="bar-label" x="${x(item.start) + 5}" y="${y + 14}">${escapeText(item.id)}</text></g>`,
        )
        .join("");
      return `<text class="station-label" x="10" y="${y + 12}">${station}</text><line class="lane-line" x1="120" x2="840" y1="${y + 11}" y2="${y + 11}"/>${blocked}${bars}`;
    })
    .join("");
  return `<svg viewBox="0 0 865 285" role="img" aria-labelledby="timeline-title timeline-description"><title id="timeline-title">${baseline ? "Greedy baseline" : "Exact plan"} contact timeline</title><desc id="timeline-description">${selected.length} displayed contacts. Each lane is a station. Horizontal positions show relative logical ticks. Full request outcomes are in the table below.</desc>${ticks}${lanes}</svg>`;
}
