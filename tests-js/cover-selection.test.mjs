import { test } from "bun:test";
import assert from "node:assert/strict";
import {
  COVER_RANK, coverAspect, isVndbCoverUrl, bestReleaseCover,
  currentCoverAspect, coverUpdateDecision, vndbCoverProvenance,
} from "../tools/cover-selection.mjs";

const url = suffix => `https://t.vndb.org/cv/01/${suffix}.jpg`;
const item = (suffix, dims, type = "pkgfront", extra = {}) =>
  ({ url: url(suffix), dims, type, vn: "v98", languages: ["ja"], ...extra });
const release = images => ({ id: "r95904", images });

test("classifies covers portrait, square, landscape and rejects unknown geometry", () => {
  assert.deepEqual(COVER_RANK, { portrait: 0, square: 1, landscape: 2 });
  assert.equal(coverAspect([600, 900]), "portrait");
  assert.equal(coverAspect([600, 690]), "portrait");
  assert.equal(coverAspect([700, 700]), "square");
  assert.equal(coverAspect([800, 716]), "square");
  assert.equal(coverAspect([282, 250]), "square");
  assert.equal(coverAspect([1920, 1080]), "landscape");
  for (const dims of [null, [], [800], [0, 800], [800, -2], [Infinity, 800], ["800", 900]]) {
    assert.equal(coverAspect(dims), null);
  }
});

test("accepts only actual HTTPS VNDB images", () => {
  assert.equal(isVndbCoverUrl(url(111)), true);
  assert.equal(isVndbCoverUrl("https://vndb.org/cv/1"), true);
  assert.equal(isVndbCoverUrl("http://t.vndb.org/cv/1"), false);
  assert.equal(isVndbCoverUrl("https://vndb.org.evil.example/cv/1"), false);
  assert.equal(isVndbCoverUrl("broken-url"), false);
});

test("chooses exact work's portrait regardless of digital/package type; square before wide", () => {
  const r = release([
    item(10, [1600, 900]),
    item(11, [900, 900]),
    item(12, [600, 900], "dig"),
    item(13, [600, 900], "pkgfront", {vn: "v999"}),
    item(14, [600, 900], "pkgfront", {languages: ["en"]}),
    { ...item(15, [600, 900]), url: "https://example.com/not-vndb.jpg" },
    item(16, null),
  ]);
  assert.deepEqual(bestReleaseCover(r, "v98"), {
    url: url(12), aspect: "portrait", type: "dig", dimensions: [600, 900],
  });
  assert.equal(bestReleaseCover(release([item(10, [1600, 900]), item(11, [900, 900])]), "v98").url, url(11));
  assert.equal(bestReleaseCover(release([item(10, [1600, 900])]), "v98").aspect, "landscape");
  assert.equal(bestReleaseCover(release([item(20, [600, 900]), item(21, [600, 900])]), "v98"), null);
  assert.equal(bestReleaseCover(release([item(20, [600, 900]), item(21, [600, 900], "dig")]), "v98").url, url(20));
  assert.equal(bestReleaseCover(null, "v98"), null);
});

test("uses verified aspect from provenance or matching release image only", () => {
  const r = release([item(31, [500, 500]), item(32, [700, 1000])]);
  assert.equal(currentCoverAspect({cover_url: "https://example.com", cover_selection: {aspect: "portrait"}}, r, "v98"), "portrait");
  assert.equal(currentCoverAspect({cover_url: "https://example.com", cover_selection: {dimensions: [500, 500]}}, r, "v98"), "square");
  assert.equal(currentCoverAspect({cover_url: url(31)}, r, "v98"), "square");
  assert.equal(currentCoverAspect({cover_url: url(31)}, r, "v999"), null);
  assert.equal(currentCoverAspect({cover_url: "https://example.com"}, r, "v98"), null);
  assert.equal(currentCoverAspect(null, r, "v98"), null);
});

test("never overwrites a better/equal or unknown existing cover", () => {
  const r = release([item(1, [600, 900]), item(2, [800, 800]), item(3, [1000, 600])]);
  const portrait = bestReleaseCover(r, "v98");
  const square = {url: url(2), aspect: "square"};
  const wide = {url: url(3), aspect: "landscape"};
  assert.equal(coverUpdateDecision(null, portrait, r, "v98").reason, "no-target-or-candidate");
  assert.equal(coverUpdateDecision({}, null, r, "v98").update, false);
  assert.equal(coverUpdateDecision({}, portrait, r, "v98").update, true);
  assert.equal(coverUpdateDecision({cover_url: url(1)}, portrait, r, "v98").reason, "already-selected");
  assert.equal(coverUpdateDecision({cover_url: "https://unknown.example/cover.jpg"}, portrait, r, "v98").reason, "unverified-current-aspect");
  assert.equal(coverUpdateDecision({cover_url: url(1)}, square, r, "v98").reason, "equal-or-worse-aspect");
  assert.equal(coverUpdateDecision({cover_url: url(2)}, square, r, "v98").reason, "already-selected");
  assert.equal(coverUpdateDecision({cover_url: url(2)}, wide, r, "v98").reason, "equal-or-worse-aspect");
  assert.equal(coverUpdateDecision({cover_url: url(2)}, portrait, r, "v98").reason, "better-aspect");
  assert.equal(coverUpdateDecision({
    cover_url: "https://publisher.example/portrait.jpg",
    cover_selection: {aspect: "portrait"},
  }, portrait, r, "v98").reason, "equal-or-worse-aspect");
  assert.equal(coverUpdateDecision({
    cover_url: "https://publisher.example/square.jpg",
    cover_selection: {aspect: "square"},
  }, portrait, r, "v98").update, true);
});

test("records exact VNDB release, shape and dimensions when updating", () => {
  const p = bestReleaseCover(release([item(123, [600, 900])]), "v98");
  assert.deepEqual(vndbCoverProvenance(p, {id: "r95904"}), {
    aspect: "portrait",
    source: "VNDB Kana exact-release cover",
    release_url: "https://vndb.org/r95904",
    image_type: "pkgfront",
    dimensions: [600, 900],
  });
});
