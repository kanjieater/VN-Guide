import { syncGeneratedFiles } from "./generate.mjs";

export async function main(
  args = [],
  {
    sync = syncGeneratedFiles,
    log = console.log,
    error = console.error,
  } = {}
) {
  const check = args.includes("--check");

  try {
    const changed = await sync(undefined, { check });
    if (check) {
      log("Generated artifacts are synchronized.");
    } else if (changed.length) {
      log(`Updated ${changed.length} generated artifact(s): ${changed.join(", ")}`);
    } else {
      log("Generated artifacts already synchronized.");
    }
    return 0;
  } catch (cause) {
    error(cause.message);
    return 1;
  }
}
