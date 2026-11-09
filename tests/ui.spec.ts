/** Production-handler, three-engine browser acceptance tests by Jason Stys.
 * Functions: ready, solve and test contracts. Variables: downloads, selectors,
 * preference/error states and keyboard/mobile layout. Lines: docs/CODE_INDEX.md.
 */
import { readFile } from "node:fs/promises";
import { expect, test, type Page } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";

/** Wait for a complete actual API-backed allocation, not just static page paint. */
async function ready(page: Page): Promise<void> {
  await page.goto("/");
  await expect(page.getByRole("status")).toContainText("Allocation complete");
}
/** Submit finite controls and wait for an evidence refresh. */
async function solve(page: Page, scenario: string): Promise<void> {
  await page.getByRole("combobox", { name: "Scenario", exact: true }).selectOption(scenario);
  await page.getByRole("button", { name: "Solve allocation" }).click();
  await expect(page.getByRole("status")).toContainText("Allocation complete");
}

test("exact plan beats greedy trap and inspection explains conflict", async ({ page }) => {
  const errors: string[] = [];
  page.on("pageerror", (error) => errors.push(error.message));
  await ready(page);
  await solve(page, "greedy-trap");
  await expect(page.getByTestId("utility")).toHaveText("120");
  await expect(page.locator("#plan-caption")).toContainText(
    "Exact plan · 120 utility · 2 contacts · 0 violations",
  );
  await page.getByRole("button", { name: "Greedy baseline", exact: true }).click();
  await expect(page.locator("#plan-caption")).toContainText(
    "Greedy baseline · 100 utility · 1 contacts",
  );
  await expect(page.getByRole("img", { name: "Greedy baseline contact timeline" })).toBeVisible();
  await page.getByRole("combobox", { name: "Candidate window", exact: true }).selectOption("A1");
  await expect(page.locator("#inspection")).toContainText("station guard conflict");
  expect(errors).toEqual([]);
});

test("station-loss comparison explains exact alternative contacts and empty service", async ({
  page,
}) => {
  await ready(page);
  await expect(page.locator("#outage-comparisons details")).toHaveCount(3);
  await solve(page, "greedy-trap");
  const alpha = page.locator("#outage-comparisons details").first();
  await alpha.locator("summary").click();
  await expect(alpha).toContainText("utility 0 (loss 120)");
  await expect(alpha).toContainText("Removed: B1, C1");
  await expect(alpha).toContainText("R02: B1 → unscheduled");
  await expect(alpha).toContainText("station-blackout");
  await expect(page.locator("#plan-caption")).toContainText("Exact plan · 120 utility");
  await solve(page, "unreachable-window");
  await expect(page.locator("#outage-comparisons summary").first()).toContainText(
    "utility 0 (loss 0)",
  );
});
test("guard boundaries, filtering and stale controls stay explicit", async ({ page }) => {
  await ready(page);
  await solve(page, "greedy-trap");
  await page.getByRole("combobox", { name: "Guard / side", exact: true }).selectOption("2");
  await expect(page.locator("#results")).toBeHidden();
  await page.getByRole("button", { name: "Solve allocation" }).click();
  await expect(page.getByTestId("utility")).toHaveText("120");
  await expect(page.locator("#timeline .contact-bar")).toHaveCount(2);
  await page.getByRole("combobox", { name: "Spacecraft filter", exact: true }).selectOption("SC-A");
  await expect(page.locator("#timeline .contact-bar")).toHaveCount(0);
  await expect(page.getByTestId("utility")).toHaveText("120");
  await expect(page.locator("#request-rows tr")).toHaveCount(3);
});

test("station outage and deadline remain visible as allocation obstacles", async ({ page }) => {
  await ready(page);
  await solve(page, "station-outage");
  await expect(page.locator("#timeline .blackout")).toHaveCount(1);
  await page.getByRole("combobox", { name: "Candidate window", exact: true }).selectOption("A2");
  await expect(page.locator("#inspection")).toContainText("station blackout");
  await solve(page, "impossible-deadline");
  await expect(page.locator("#request-rows tr").filter({ hasText: "R08" })).toContainText(
    "Unscheduled",
  );
  await page.getByRole("combobox", { name: "Candidate window", exact: true }).selectOption("H1");
  await expect(page.locator("#inspection")).toContainText("request time window");
});

test("all stations blocked gives a feasible empty plan, not a missing result", async ({ page }) => {
  await ready(page);
  await solve(page, "unreachable-window");
  await expect(page.getByTestId("utility")).toHaveText("0");
  await expect(page.locator("#timeline .blackout")).toHaveCount(3);
  await expect(page.locator("#plan-caption")).toContainText("0 contacts · 0 violations");
  await expect(page.locator("#request-rows tr")).toHaveCount(8);
  await expect(page.locator("#coverage")).toHaveText("8 unscheduled");
});

test("four real downloads contain consistent complete input and evidence", async ({ page }) => {
  await ready(page);
  await solve(page, "greedy-trap");
  for (const [name, file, snippet] of [
    ["Full JSON", "scheduler-evidence.json", '"utility": 120'],
    ["Candidate CSV", "scheduler-candidates.csv", "A1,R01,ALPHA"],
    ["HTML report", "scheduler-evidence.html", "Contact planning evidence"],
    ["Input JSON", "scheduler-input.json", '"horizon": 120'],
  ] as const) {
    const wait = page.waitForEvent("download");
    await page.getByRole("link", { name: `${name} ↓`, exact: true }).click();
    const download = await wait;
    expect(download.suggestedFilename()).toBe(file);
    const path = await download.path();
    expect(path).not.toBeNull();
    expect(await readFile(path!, "utf8")).toContain(snippet);
  }
});

test("API failure hides evidence and manual retry recovers", async ({ page }) => {
  await page.route("**/api/run?**", (route) => route.fulfill({ status: 503, body: "Unavailable" }));
  await page.goto("/");
  await expect(page.getByRole("alert")).toBeVisible();
  await expect(page.locator("#results")).toBeHidden();
  await page.unroute("**/api/run?**");
  await page.getByRole("button", { name: "Retry allocation" }).click();
  await expect(page.getByRole("status")).toContainText("Allocation complete");
  await expect(page.getByRole("alert")).toBeHidden();
});

test("unexpected markup in API numeric fields remains inert", async ({ page }) => {
  const payload = '<img src=x onerror="alert(1)">';
  await page.route("**/api/run?**", async (route) => {
    const response = await route.fetch();
    const body = await response.json();
    body.exact.utility = payload;
    body.station_usage[0].used = payload;
    body.requests[0].release = payload;
    await route.fulfill({ response, json: body });
  });
  await ready(page);
  await expect(page.getByTestId("utility")).toHaveText(payload);
  await expect(page.locator("#results img")).toHaveCount(0);
  await expect(page.locator("#budgets")).toContainText(payload);
  await expect(page.locator("#request-rows")).toContainText(payload);
});

test("optional preferences, mobile layout, accessibility and security headers", async ({
  page,
  request,
}) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await ready(page);
  expect(await page.evaluate(() => localStorage.length)).toBe(0);
  await page.getByRole("checkbox", { name: "Remember these controls" }).check();
  await solve(page, "greedy-trap");
  await page.reload();
  await expect(page.getByRole("status")).toContainText("Allocation complete");
  await expect(page.getByRole("combobox", { name: "Scenario", exact: true })).toHaveValue(
    "greedy-trap",
  );
  await page.getByRole("checkbox", { name: "Remember these controls" }).uncheck();
  expect(await page.evaluate(() => localStorage.length)).toBe(0);
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(
    true,
  );
  const scan = await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa", "wcag21aa"]).analyze();
  expect(scan.violations).toEqual([]);
  await page.getByRole("region", { name: "Scrollable request coverage" }).focus();
  await page.keyboard.press("ArrowRight");
  await expect(page.getByRole("region", { name: "Scrollable request coverage" })).toBeFocused();
  const response = await request.get("/api/health");
  expect(response.headers()["content-security-policy"]).toContain("frame-ancestors 'none'");
  await page.getByRole("combobox", { name: "Scenario", exact: true }).focus();
  await page.keyboard.press("Tab");
  await expect(page.getByRole("combobox", { name: "Guard / side", exact: true })).toBeFocused();
});
