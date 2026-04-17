import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const ROOT = path.resolve(__dirname, '..')
const SUMMARY = path.join(ROOT, 'coverage', 'coverage-summary.json')

function fail(message) {
  process.stderr.write(`${message}\n`)
  process.exit(1)
}

if (!fs.existsSync(SUMMARY)) {
  fail(`Missing coverage summary: ${SUMMARY}. Run: npm test -- --coverage`)
}

const raw = fs.readFileSync(SUMMARY, 'utf8')
const data = JSON.parse(raw)
const total = data?.total
if (!total) {
  fail(`Invalid coverage summary (missing "total"): ${SUMMARY}`)
}

const thresholds = {
  lines: 70,
  statements: 70,
  functions: 60,
  branches: 50,
}

const actual = {
  lines: total.lines?.pct ?? null,
  statements: total.statements?.pct ?? null,
  functions: total.functions?.pct ?? null,
  branches: total.branches?.pct ?? null,
}

for (const [key, min] of Object.entries(thresholds)) {
  const pct = actual[key]
  if (typeof pct !== 'number') {
    fail(`Invalid coverage summary (missing ${key}.pct): ${SUMMARY}`)
  }
  if (pct < min) {
    fail(`Coverage gate failed: ${key} ${pct}% < ${min}%`)
  }
}

process.stdout.write(
  `Coverage gate OK: lines ${actual.lines}%, statements ${actual.statements}%, functions ${actual.functions}%, branches ${actual.branches}%\n`,
)
