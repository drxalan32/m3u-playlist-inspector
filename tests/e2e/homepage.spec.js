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
