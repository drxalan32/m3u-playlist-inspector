const { test, expect } = require("@playwright/test");

test.beforeEach(async ({ page }) => {
  await page.goto("/");
});

test("homepage loads and theme toggle switches modes", async ({ page }) => {
  await expect(page).toHaveTitle(/M3U/i);
  const toggle = page.locator("#theme-toggle");
  await expect(toggle).toBeVisible();
  await toggle.click();
  await expect(page.locator("html")).toHaveAttribute("data-theme", "dark");
  await toggle.click();
  await expect(page.locator("html")).toHaveAttribute("data-theme", "light");
});

test("playlist generator adds, edits, deletes and undoes entries", async ({ page }) => {
  await page.locator("#generator-name").fill("News Channel");
  await page.locator("#generator-url").fill("https://example.com/news.m3u8");
  await page.locator("#generator-duration").selectOption("-1");
  await page.locator("#generator-add").click();
  await expect(page.locator("#generator-count")).toHaveText("1");
  await expect(page.locator("#generator-entry-list")).toContainText("News Channel");

  await page.getByRole("button", { name: "Edit" }).click();
  await page.locator("#generator-name").fill("Updated News");
  await page.locator("#generator-add").click();
  await expect(page.locator("#generator-entry-list")).toContainText("Updated News");

  await page.getByRole("button", { name: "Delete" }).click();
  await expect(page.locator("#generator-count")).toHaveText("0");
  await page.locator("#generator-undo").click();
  await expect(page.locator("#generator-count")).toHaveText("1");
  await expect(page.locator("#generator-entry-list")).toContainText("Updated News");
});

test("imports an M3U file and exports a playlist", async ({ page }) => {
  const file = {
    name: "sample.m3u",
    mimeType: "audio/x-mpegurl",
    buffer: Buffer.from("#EXTM3U\n#EXTINF:-1,Sample Channel\nhttps://example.com/sample.m3u8\n")
  };
  await page.locator("#generator-import-file").setInputFiles(file);
  await expect(page.locator("#generator-count")).toHaveText("1");
  await expect(page.locator("#generator-preview")).toHaveValue(/Sample Channel/);
  const downloadPromise = page.waitForEvent("download");
  await page.locator("#generator-download").click();
  const download = await downloadPromise;
  expect(download.suggestedFilename()).toBe("my-playlist.m3u");
});

test("validation detects duplicate URLs and removes duplicates with confirmation", async ({ page }) => {
  const file = {
    name: "duplicates.m3u",
    mimeType: "audio/x-mpegurl",
    buffer: Buffer.from("#EXTM3U\n#EXTINF:-1,First\nhttps://example.com/shared.m3u8\n#EXTINF:-1,Second\nhttps://example.com/shared.m3u8\n")
  };
  await page.locator("#generator-import-file").setInputFiles(file);
  await page.locator("#generator-validate").click();
  await expect(page.locator("#generator-validation-warnings")).toContainText("1 warnings");
  page.once("dialog", dialog => dialog.accept());
  await page.locator("#generator-remove-duplicates").click();
  await expect(page.locator("#generator-count")).toHaveText("1");
});

test("safe fixes normalize malformed imported durations", async ({ page }) => {
  const file = {
    name: "needs-fixes.m3u",
    mimeType: "audio/x-mpegurl",
    buffer: Buffer.from("#EXTM3U\n#EXTINF:bad,Channel\nhttps://example.com/channel.m3u8\n")
  };
  await page.locator("#generator-import-file").setInputFiles(file);
  await expect(page.locator("#generator-count")).toHaveText("1");
  await page.locator("#generator-validate").click();
  await expect(page.locator("#generator-validation-warnings")).toContainText("1 warnings");
  await page.locator("#generator-auto-fix").click();
  await expect(page.locator("#generator-preview")).toHaveValue(/#EXTINF:-1/);
});

test("exports CSV and JSON reports", async ({ page }) => {
  await page.locator("#generator-name").fill("Export Channel");
  await page.locator("#generator-url").fill("https://example.com/export.m3u8");
  await page.locator("#generator-add").click();
  for (const [selector, filename] of [
    ["#generator-export-csv", "m3u-playlist-report.csv"],
    ["#generator-export-json", "m3u-playlist-report.json"]
  ]) {
    const downloadPromise = page.waitForEvent("download");
    await page.locator(selector).click();
    const download = await downloadPromise;
    expect(download.suggestedFilename()).toBe(filename);
  }
});


test("search and group filters show only matching playlist entries", async ({ page }) => {
  const file = {
    name: "filters.m3u",
    mimeType: "audio/x-mpegurl",
    buffer: Buffer.from("#EXTM3U\n#EXTINF:-1 group-title=\"Sports\",Football\nhttps://example.com/football.m3u8\n#EXTINF:-1 group-title=\"News\",World News\nhttps://example.com/news.m3u8\n")
  };
  await page.locator("#generator-import-file").setInputFiles(file);
  const rows = page.locator("#generator-entry-list .generator-entry");
  await expect(rows).toHaveCount(2);
  await page.locator("#generator-search").fill("Football");
  await expect(rows).toHaveCount(1);
  await expect(rows.first()).toContainText("Football");
  await page.locator("#generator-search").fill("");
  await page.locator("#generator-filter-group").selectOption({ label: "News" });
  await expect(rows).toHaveCount(1);
  await expect(rows.first()).toContainText("World News");
});

test("bulk selection updates group and renames selected entries", async ({ page }) => {
  const file = {
    name: "bulk.m3u",
    mimeType: "audio/x-mpegurl",
    buffer: Buffer.from("#EXTM3U\n#EXTINF:-1,Alpha Channel\nhttps://example.com/alpha.m3u8\n#EXTINF:-1,Beta Channel\nhttps://example.com/beta.m3u8\n")
  };
  await page.locator("#generator-import-file").setInputFiles(file);
  await page.locator("#generator-select-visible").click();
  await expect(page.locator("#generator-selection-status")).toContainText("2 entries selected");
  await page.locator("#generator-bulk-group").fill("Favorites");
  await page.locator("#generator-apply-group").click();
  await expect(page.locator("#generator-entry-list")).toContainText("Favorites");
  // Applying a bulk group intentionally clears selection; select entries again before renaming.
  await page.locator("#generator-select-visible").click();
  await expect(page.locator("#generator-selection-status")).toContainText("2 entries selected");
  await page.locator("#generator-rename-find").fill("Channel");
  await page.locator("#generator-rename-replace").fill("Station");
  await page.locator("#generator-apply-rename").click();
  await expect(page.locator("#generator-entry-list")).toContainText("Alpha Station");
  await expect(page.locator("#generator-entry-list")).toContainText("Beta Station");
});

test("keyboard shortcut reorders the focused playlist entry", async ({ page }) => {
  const file = {
    name: "keyboard.m3u",
    mimeType: "audio/x-mpegurl",
    buffer: Buffer.from("#EXTM3U\n#EXTINF:-1,First\nhttps://example.com/first.m3u8\n#EXTINF:-1,Second\nhttps://example.com/second.m3u8\n")
  };
  await page.locator("#generator-import-file").setInputFiles(file);
  const firstRow = page.locator("#generator-entry-list .generator-entry").first();
  await firstRow.focus();
  await page.keyboard.press("Alt+ArrowDown");
  await expect(page.locator("#generator-entry-list .generator-entry").first()).toContainText("Second");
  await page.locator("#generator-undo").click();
  await expect(page.locator("#generator-entry-list .generator-entry").first()).toContainText("First");
});

test("drag and drop reorders playlist entries", async ({ page }) => {
  const file = {
    name: "drag.m3u",
    mimeType: "audio/x-mpegurl",
    buffer: Buffer.from("#EXTM3U\n#EXTINF:-1,First\nhttps://example.com/first.m3u8\n#EXTINF:-1,Second\nhttps://example.com/second.m3u8\n#EXTINF:-1,Third\nhttps://example.com/third.m3u8\n")
  };
  await page.locator("#generator-import-file").setInputFiles(file);
  const rows = page.locator("#generator-entry-list .generator-entry");
  await rows.nth(0).dragTo(rows.nth(2));
  await expect(rows.first()).toContainText("Second");
  await expect(rows.nth(2)).toContainText("First");
});

test("dedicated M3U editor page embeds and runs the existing editor", async ({ page }) => {
  await page.goto("/m3u-playlist-editor.html");
  await expect(page).toHaveTitle(/M3U Editor Online/i);
  await expect(page.locator("h1")).toContainText("M3U Editor Online");
  await expect(page.locator("#playlist-generator")).toHaveCount(1);
  await expect(page.locator("#generator-import-file")).toBeVisible();
  await expect(page.locator("#generator-entry-list")).toBeVisible();

  const file = {
    name: "dedicated-editor-test.m3u",
    mimeType: "audio/x-mpegurl",
    buffer: Buffer.from("#EXTM3U\\n#EXTINF:-1 group-title=\"News\",Test Channel\\nhttps://example.com/test.m3u8\\n")
  };
  await page.locator("#generator-import-file").setInputFiles(file);
  await expect(page.locator("#generator-count")).toHaveText("1");
  await expect(page.locator("#generator-entry-list")).toContainText("Test Channel");

  const downloadPromise = page.waitForEvent("download");
  await page.locator("#generator-download").click();
  const download = await downloadPromise;
  expect(download.suggestedFilename()).toBe("my-playlist.m3u");
});
