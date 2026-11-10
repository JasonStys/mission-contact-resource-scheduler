/** Jason Stys — actual extracted contact scheduler, station-loss comparison and JSON export.
 * Functions: owned journey; variables: independent trap oracle, baseline and outage deltas.
 * Exact lines: docs/CODE_INDEX.md. Finite educational allocation, no radio or mission dispatch.
 */
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import path from "node:path";
import { expect } from "@playwright/test";
import { runNativeJourney } from "./native_browser.mjs";

await runNativeJourney(async ({ page, request, outputDirectory, version }) => {
  const status = page.getByRole("status");
  await expect(status).toContainText("Allocation complete");
  await page.getByRole("combobox", { name: "Scenario", exact: true }).selectOption("greedy-trap");
  await page.getByRole("button", { name: "Solve allocation" }).click();
  await expect(page.getByTestId("utility")).toHaveText("120");
  const response = await request.get("api/run?scenario=greedy-trap");
  assert.equal(response.status(), 200);
  const run = await response.json();
  assert.equal(run.version, version);
  assert.deepEqual(run.exact.selected, ["B1", "C1"]);
  assert.equal(run.exact.utility, 60 + 60);
  assert.equal(run.greedy.utility, 100);
  const alpha = run.outage_comparisons.find((row) => row.station === "ALPHA");
  assert.deepEqual(
    [alpha.exact.selected, alpha.removed, alpha.utility_loss],
    [[], ["B1", "C1"], 120],
  );
  assert.deepEqual(alpha.request_changes, [
    { request: "R02", before: "B1", after: null },
    { request: "R03", before: "C1", after: null },
  ]);
  const comparison = page.locator("#outage-comparisons details").first();
  await comparison.locator("summary").click();
  await expect(comparison).toContainText("utility 0 (loss 120)");
  await expect(comparison).toContainText("Removed: B1, C1");
  await expect(page.locator("#plan-caption")).toContainText("Exact plan · 120 utility");
  const pending = page.waitForEvent("download");
  await page.getByRole("link", { name: "Full JSON ↓", exact: true }).click();
  const download = await pending;
  const file = path.join(outputDirectory, "native-contact-evidence.json");
  await download.saveAs(file);
  assert.deepEqual(JSON.parse(await readFile(file, "utf8")), run);
  await page
    .getByRole("combobox", { name: "Scenario", exact: true })
    .selectOption("unreachable-window");
  await page.getByRole("button", { name: "Solve allocation" }).click();
  await expect(page.getByTestId("utility")).toHaveText("0");
  await expect(page.locator("#outage-comparisons summary").first()).toContainText(
    "utility 0 (loss 0)",
  );
  assert.equal((await request.get("api/run?guard=99")).status(), 400);
});
