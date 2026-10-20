/** Pure finite-setting, escaping and SVG contract tests by Jason Stys.
 * Variables: bounded API stubs and hostile preference text. Lines: docs/CODE_INDEX.md.
 */
import { describe, expect, it } from "vitest";
import {
  defaults,
  escapeText,
  query,
  readPreferences,
  timelineMarkup,
  type Evidence,
} from "./contracts";

describe("finite preferences", () => {
  it("round-trips all reviewed defaults", () => {
    expect(readPreferences(JSON.stringify(defaults))).toEqual(defaults);
  });
  it.each([null, "not json", "[]", "null", "{}", '"text"', "x".repeat(513)])(
    "rejects malformed input %s",
    (raw) => {
      expect(readPreferences(raw)).toBeNull();
    },
  );
  it("rejects coercion, unknown keys and prototype names", () => {
    for (const changes of [
      { guard: "1" },
      { policy: true },
      { scenario: "toString" },
      { extra: 1 },
      { station_budget: 10 },
    ])
      expect(readPreferences(JSON.stringify({ ...defaults, ...changes }))).toBeNull();
  });
  it("creates only the finite relative query", () => {
    expect(new URLSearchParams(query(defaults)).get("scenario")).toBe("nominal");
    expect(new URLSearchParams(query(defaults)).size).toBe(5);
  });
});
describe("inert rendering", () => {
  it("escapes text and both quote types", () => {
    expect(escapeText('<script a="x">&\'</script>')).toBe(
      "&lt;script a=&quot;x&quot;&gt;&amp;&#39;&lt;/script&gt;",
    );
  });
  it("draws selected contacts, guards, lanes and blackouts without inline styles", () => {
    const run = {
      settings: defaults,
      exact: { selected: ["A"] },
      greedy: { selected: [] },
      candidates: [
        { id: "A", request: "R1", spacecraft: "SC-A", station: "ALPHA", start: 10, end: 20 },
      ],
      case: { blackouts: [{ station: "BRAVO", start: 0, end: 120 }] },
    } as unknown as Evidence;
    const markup = timelineMarkup(run, false, "ALL");
    expect(markup).toContain('x="174"');
    expect(markup).toContain("ALPHA");
    expect(markup).toContain("UNAVAILABLE");
    expect(markup).not.toContain("style=");
    expect(timelineMarkup(run, false, "SC-B")).not.toContain('class="contact-bar"');
    expect(timelineMarkup(run, true, "ALL")).toContain("Greedy baseline contact timeline");
  });
});
