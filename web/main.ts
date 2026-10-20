/** Interactive local planning workspace by Jason Stys.
 * Functions: solveAllocation, render, inspect, displayTimeline, configurePreferences.
 * Variables: current evidence, abort/generation tokens and finite form state.
 * DOM/variable lines: docs/CODE_INDEX.md; no external requests or implicit persistence.
 */
import "./style.css";
import {
  choices,
  defaults,
  escapeText as esc,
  query,
  readPreferences,
  timelineMarkup,
  type Evidence,
  type Settings,
} from "./contracts";

/** Resolve only known static DOM IDs, failing immediately if a template contract drifts. */
function element<T extends HTMLElement>(id: string): T {
  const node = document.getElementById(id);
  if (!node) throw new Error("Missing UI element");
  return node as T;
}
const controls = element<HTMLFormElement>("controls");
const status = element("status");
const remember = element<HTMLInputElement>("remember");
const preferenceKey = "contact-scheduler-controls-v1";
let current: Evidence | null = null;
let baseline = false;
let generation = 0;
let pending: AbortController | null = null;

/** Read finite values from selects, never from URL parameters or free-form HTML. */
function settings(): Settings {
  return {
    scenario: element<HTMLSelectElement>("scenario").value,
    ...Object.fromEntries(
      Object.keys(choices).map((key) => [key, Number(element<HTMLSelectElement>(key).value)]),
    ),
  } as Settings;
}

/** Show optional preference failures non-disruptively; scheduling does not require browser storage. */
function savePreferences(): void {
  try {
    if (remember.checked) localStorage.setItem(preferenceKey, JSON.stringify(settings()));
    else localStorage.removeItem(preferenceKey);
  } catch {
    status.textContent =
      "Browser storage is unavailable. The planner still works without saving controls.";
  }
}

/** Restore only allowlisted settings; malformed/blocked storage falls back to reviewed defaults. */
function configurePreferences(): void {
  let restored: Settings | null = null;
  try {
    restored = readPreferences(localStorage.getItem(preferenceKey));
  } catch {
    /* Private browsing may block storage; defaults remain usable. */
  }
  remember.checked = restored !== null;
  for (const [key, value] of Object.entries(restored ?? defaults))
    element<HTMLSelectElement>(key).value = String(value);
  remember.addEventListener("change", savePreferences);
}

/** Render the selected contact's documented final-plan obstacles, not a fabricated causal proof. */
function inspect(): void {
  if (!current) return;
  const item = current.candidates.find(
    (candidate) => candidate.id === element<HTMLSelectElement>("candidate").value,
  );
  if (!item) {
    element("inspection").textContent =
      "No candidate windows in this case. Requests remain visible below.";
    return;
  }
  const req = current.requests.find((request) => request.id === item.request)!;
  element("inspection").innerHTML =
    `<p class="decision ${item.selected ? "accepted" : "deferred"}">${item.selected ? "SELECTED IN EXACT PLAN" : "NOT SELECTED IN EXACT PLAN"}</p><h3>${esc(item.request)} / ${esc(item.spacecraft)} → ${esc(item.station)}</h3><dl class="facts"><div><dt>Transmission</dt><dd>[${esc(item.start)}, ${esc(item.end)})</dd></div><div><dt>Station reservation</dt><dd>[${esc(item.start - current.settings.guard)}, ${esc(item.end + current.settings.guard)})</dd></div><div><dt>Required window</dt><dd>[${esc(req.release)}, ${esc(req.deadline)})</dd></div><div><dt>Data / capacity</dt><dd>${esc(req.units)} / ${esc((item.end - item.start) * item.rate)} units</dd></div><div><dt>Energy / band</dt><dd>${esc(item.energy)} units / ${esc(req.band)}</dd></div><div><dt>Greedy baseline</dt><dd>${item.baseline ? "Selected" : "Not selected"}</dd></div></dl>${item.selected ? '<p class="inspector-note">Passes all constraints within the complete exact allocation.</p>' : `<ul class="reasons">${item.reasons.map((reason) => `<li>${esc(reason.replaceAll("-", " "))}</li>`).join("")}</ul><p class="inspector-note">Obstacles relative to the final exact plan. This is not a minimal conflict set or the only possible allocation.</p>`}`;
}

/** Switch drawing only; exact-plan budget/request summaries and exports retain their labels. */
function displayTimeline(): void {
  if (!current) return;
  element("timeline").innerHTML = timelineMarkup(
    current,
    baseline,
    element<HTMLSelectElement>("craft-filter").value,
  );
  element("exact-view").setAttribute("aria-pressed", String(!baseline));
  element("greedy-view").setAttribute("aria-pressed", String(baseline));
  const plan = baseline ? current.greedy : current.exact;
  element("plan-caption").textContent =
    `${baseline ? "Greedy baseline" : "Exact plan"} · ${plan.utility} utility · ${plan.fulfilled} contacts · ${plan.violations.length} violations`;
}

/** Render bounded escaped evidence and fixed same-origin downloads; never persist reports. */
function render(run: Evidence): void {
  const exact = run.exact;
  element("metrics").innerHTML =
    `<article><p>EXACT UTILITY</p><strong data-testid="utility">${esc(exact.utility)}</strong><span>${run.settings.policy ? "priority × delivered data" : "delivered data units"}</span></article><article><p>VS. GREEDY BASELINE</p><strong class="teal">+${esc(run.delta)}</strong><span>baseline utility ${esc(run.greedy.utility)}</span></article><article><p>REQUESTS FULFILLED</p><strong>${esc(exact.fulfilled)}<small> / ${esc(run.requests.length)}</small></strong><span>${esc(exact.units)} data units delivered</span></article><article><p>CONSTRAINT AUDIT</p><strong>${esc(exact.violations.length)}<small> violations</small></strong><span>finite-candidate optimum · ${esc(exact.visited_nodes)} search nodes</span></article>`;
  const selected = element<HTMLSelectElement>("candidate");
  const previous = selected.value;
  selected.innerHTML = run.candidates
    .map(
      (item) =>
        `<option value="${esc(item.id)}">${esc(item.id)} · ${esc(item.request)} / ${esc(item.station)} · ${item.selected ? "selected" : "not selected"}</option>`,
    )
    .join("");
  if (run.candidates.some((item) => item.id === previous)) selected.value = previous;
  selected.disabled = run.candidates.length === 0;
  element("budgets").innerHTML = [
    ["Station occupancy / ticks", run.station_usage],
    ["Spacecraft energy / units", run.energy_usage],
  ]
    .map(
      ([title, rows]) =>
        `<h3 class="budget-title">${esc(title)}</h3>${(rows as Evidence["station_usage"]).map((item) => `<div class="budget-row"><div><label for="budget-${esc(item.name)}">${esc(item.name)}</label><span>${esc(item.used)} / ${esc(item.budget)}</span></div><progress id="budget-${esc(item.name)}" max="${esc(item.budget)}" value="${esc(item.used)}">${esc(item.used)} of ${esc(item.budget)}</progress></div>`).join("")}`,
    )
    .join("");
  element("request-rows").innerHTML = run.requests
    .map(
      (req) =>
        `<tr><th scope="row">${esc(req.id)} <span>${esc(req.spacecraft)} · ${esc(req.band)}</span></th><td>[${esc(req.release)}, ${esc(req.deadline)})</td><td>${esc(req.units)} units <span>priority ${esc(req.priority)}</span></td><td><span class="outcome ${req.selected ? "yes" : "no"}">${esc(req.selected ?? "Unscheduled")}</span><span>${req.alternatives.length ? esc(req.alternatives.join(" / ")) : "No candidate windows"}</span></td></tr>`,
    )
    .join("");
  element("coverage").textContent = `${run.requests.length - exact.fulfilled} unscheduled`;
  element("downloads").innerHTML = [
    ["json", "Full JSON"],
    ["csv", "Candidate CSV"],
    ["html", "HTML report"],
    ["input", "Input JSON"],
  ]
    .map(
      ([format, label]) =>
        `<a download href="/api/report?${esc(query(settings()))}&amp;format=${format}">${label} ↓</a>`,
    )
    .join("");
  element("evidence-id").textContent = `SHA-256 / ${run.id}`;
  displayTimeline();
  inspect();
}

/** Cancel superseded requests and hide stale results on failure; no retry loop or external fallback. */
async function solveAllocation(): Promise<void> {
  pending?.abort();
  pending = new AbortController();
  const token = ++generation;
  element("results").hidden = true;
  element("error").hidden = true;
  status.textContent = "Solving the finite allocation and auditing all constraints…";
  const button = element<HTMLButtonElement>("run-button");
  button.disabled = true;
  try {
    const response = await fetch(`/api/run?${query(settings())}`, {
      signal: pending.signal,
      credentials: "omit",
    });
    if (!response.ok) throw new Error("Local service unavailable");
    const run = (await response.json()) as Evidence;
    if (token !== generation) return;
    current = run;
    baseline = false;
    render(run);
    element("results").hidden = false;
    status.textContent = `Allocation complete. ${run.exact.fulfilled} of ${run.requests.length} optional requests fulfilled; ${run.exact.violations.length} constraint violations.`;
    if (remember.checked) savePreferences();
  } catch (error) {
    if (token !== generation || (error instanceof DOMException && error.name === "AbortError"))
      return;
    current = null;
    element("error").hidden = false;
    status.textContent = "Allocation unavailable. Retry when the local service is ready.";
  } finally {
    if (token === generation) button.disabled = false;
  }
}

controls.addEventListener("submit", (event) => {
  event.preventDefault();
  void solveAllocation();
});
controls.addEventListener("change", () => {
  element("results").hidden = true;
  status.textContent = "Controls changed. Solve allocation to refresh all results and exports.";
  pending?.abort();
  generation++;
  element<HTMLButtonElement>("run-button").disabled = false;
});
element("retry").addEventListener("click", () => {
  void solveAllocation();
});
element("candidate").addEventListener("change", inspect);
element("craft-filter").addEventListener("change", displayTimeline);
element("exact-view").addEventListener("click", () => {
  baseline = false;
  displayTimeline();
});
element("greedy-view").addEventListener("click", () => {
  baseline = true;
  displayTimeline();
});
configurePreferences();
void solveAllocation();
