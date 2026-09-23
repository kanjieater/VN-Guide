import { rm } from "node:fs/promises";

const withCoverage = process.argv.includes("--coverage");

const shards = [
  {
    name: "guide-app",
    files: ["tests-js/guide-app.use-cases.test.mjs"],
    concurrent: false,
  },
  {
    name: "flowchart",
    files: ["tests-js/flowchart.use-cases.test.mjs"],
    concurrent: false,
  },
  {
    name: "sidecars",
    files: ["tests-js/flowchart.sidecars.test.mjs"],
    concurrent: false,
  },
  {
    name: "core",
    files: [
      "tests-js/diff-coverage.test.mjs",
      "tests-js/generator.test.mjs",
      "tests-js/landing.use-cases.test.mjs",
      "tests-js/repository.contracts.test.mjs",
    ],
    concurrent: true,
  },
];

if (withCoverage) {
  await rm("coverage", { recursive: true, force: true });
}

function commandFor(shard) {
  const command = ["bun", "test", ...shard.files];
  if (shard.concurrent) {
    command.push("--concurrent", "--max-concurrency=20");
  }
  if (withCoverage) {
    command.push(
      "--coverage",
      "--coverage-reporter=text",
      "--coverage-reporter=lcov",
      `--coverage-dir=coverage/${shard.name}`
    );
  }
  return command;
}

console.log(`Running ${shards.length} isolated Bun test shards in parallel...`);

const processes = shards.map(shard => ({
  shard,
  process: Bun.spawn(commandFor(shard), {
    stdout: "inherit",
    stderr: "inherit",
  }),
}));

const results = await Promise.all(
  processes.map(async ({ shard, process }) => ({
    shard: shard.name,
    exitCode: await process.exited,
  }))
);

const failed = results.filter(result => result.exitCode !== 0);
if (failed.length) {
  console.error(
    `Failed shard(s): ${failed.map(result => result.shard).join(", ")}`
  );
  process.exit(1);
}

console.log("All Bun test shards passed.");
