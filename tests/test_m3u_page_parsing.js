"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const root = path.resolve(__dirname, "..");
const read = (file) => fs.readFileSync(path.join(root, file), "utf8");
const extract = (source, pattern, label) => {
  const match = source.match(pattern);
  assert.ok(match, label + " function was not found");
  return match[0];
};
const loadFunction = (source, pattern, label, ...args) => {
  const declaration = extract(source, pattern, label);
  return new Function(...args.map((_, i) => "arg" + i), "return (" + declaration + ");")(...args);
};
const sample = (ending) => [
  '#eXtMmLu x-tvg-url="https://guide.example/epg.xml"',
  '#eXtInF:-1 tvg-id="a" group-title="News, Sports",BBC One',
  "https://example.com/live.m3u8",
  ""
].join(ending);

const analyzer = read("docs/m3u-playlist-analyzer.html");
const analyzerParseSource = analyzer.slice(analyzer.indexOf("function parse(text){"), analyzer.indexOf("function analyse(text){")).trim();
const analyzerParse = new Function("return (" + analyzerParseSource + ");")();
const analyzerCsv = loadFunction(analyzer, /function csvCell\(v\)\{[^\n]*\}/, "analyzer csvCell");
for (const ending of ["\n", "\r", "\r\n"]) {
  const entries = analyzerParse(sample(ending));
  assert.equal(entries.length, 1);
  assert.equal(entries[0].name, "BBC One");
  assert.equal(entries[0].category, "News, Sports");
  assert.equal(entries[0].hasExtinf, true);
}
assert.equal(analyzerCsv("-1"), '"-1"');
assert.equal(analyzerCsv("12.5"), '"12.5"');
assert.equal(analyzerCsv("=1+1"), '"\'=1+1"');
assert.equal(analyzerCsv("+SUM(A1:A2)"), '"\'+SUM(A1:A2)"');
assert.equal(analyzerCsv("@cmd"), '"\'@cmd"');
assert.equal(analyzerCsv("\tvalue"), '"\'\tvalue"');
assert.equal(analyzerCsv("\rvalue"), '"\'\rvalue"');
console.log("PASS analyzer: EXTINF parsing, header attributes, line endings and CSV formula protection");

const converter = read("docs/m3u-playlist-converter.html");
const attr = loadFunction(converter, /function attr\(line,key\)\{[^\n]*\}/, "converter attr");
const converterParseStart = converter.indexOf("function parseM3U(text){");
const converterParseSource = converter.slice(converterParseStart, converter.indexOf("\n", converterParseStart)).trim();
const converterParse = new Function("attr", "return (" + converterParseSource + ");")(attr);
const converterCsv = loadFunction(converter, /function csvCell\(v\)\{[^\n]*\}/, "converter csvCell");
for (const ending of ["\n", "\r", "\r\n"]) {
  const entries = converterParse(sample(ending));
  assert.equal(entries.length, 1);
  assert.equal(entries[0].name, "BBC One");
  assert.equal(entries[0].groupTitle, "News, Sports");
}
assert.equal(converterCsv("-1"), "-1");
assert.equal(converterCsv("12.5"), "12.5");
assert.equal(converterCsv("=1+1"), "'=1+1");
assert.equal(converterCsv("+SUM(A1:A2)"), "'+SUM(A1:A2)");
assert.equal(converterCsv("@cmd"), "'@cmd");
assert.equal(converterCsv("\tvalue"), "'\tvalue");
assert.equal(converterCsv("\rvalue"), "'" + "\rvalue" + '"');
console.log("PASS converter: EXTINF parsing, header attributes, line endings and CSV formula protection");

const merger = read("docs/m3u-playlist-merger.html");
const mergerParse = loadFunction(merger, /function parseEntries\(text\)\{[^\n]*\}/, "merger parseEntries");
for (const ending of ["\n", "\r", "\r\n"]) {
  const entries = mergerParse(sample(ending));
  assert.equal(entries.length, 1);
  assert.deepEqual(entries[0].metadata, ['#eXtInF:-1 tvg-id="a" group-title="News, Sports",BBC One']);
}
assert.match(merger, /for\(const entry of parseEntries\(t\)\)all\.push\(entry\)/);
assert.doesNotMatch(merger, /all\.push\(\.\.\.parseEntries/);
assert.doesNotMatch(merger, /output\.push\(\.\.\.e\.metadata/);
console.log("PASS merger: header attributes, metadata preservation, line endings and loop-based accumulation");
