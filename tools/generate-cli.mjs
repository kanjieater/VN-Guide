import { syncGeneratedFiles } from "./generate.mjs";

const check = process.argv.includes("--check");

try {
  const changed = await syncGeneratedFiles(undefined, { check });
  if (check) {
    console.log("Generated artifacts are synchronized.");
  } else if (changed.length) {
    console.log(`Updated ${changed.length} generated artifact(s): ${changed.join(", ")}`);
  } else {
    console.log("Generated artifacts already synchronized.");
  }
} catch (error) {
  console.error(error.message);
  process.exit(1);
}
