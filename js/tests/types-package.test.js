import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import test from 'node:test';

const packageJsonUrl = new URL('../package.json', import.meta.url);

test('package publishes a TypeScript declaration entry point', async () => {
  const packageJson = JSON.parse(await readFile(packageJsonUrl, 'utf8'));

  assert.equal(packageJson.types, 'src/index.d.ts');
  await assert.doesNotReject(() => readFile(new URL('../src/index.d.ts', import.meta.url), 'utf8'));
});
