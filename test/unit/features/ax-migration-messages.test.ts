/**
 * Every key the AX migration result can show has a message in each locale, and no message is
 * left behind when a key is removed.
 */
import { AX_PLATFORMS } from '@/lib/features/diagnostics/ax-migration/definition';
import {
  AX_CHECKPOINT_KEYS,
  AX_REASON_KEYS,
} from '@/lib/features/diagnostics/ax-migration/evaluate';
import { TARGET_SYSTEMS } from '@/lib/features/leads/types/pipeline';
import en from '@/locales/en/common.json';
import ja from '@/locales/ja/common.json';
import { describe, expect, it } from 'vitest';

const sorted = (keys: readonly string[]) => [...keys].sort();

describe.each([
  ['ja', ja],
  ['en', en],
])('AX migration messages (%s)', (_locale, messages) => {
  const result = messages.axDiagnosis.result;

  it('has exactly one message per reason', () => {
    expect(sorted(Object.keys(result.reasons))).toEqual(sorted(AX_REASON_KEYS));
  });

  it('has exactly one message per checkpoint', () => {
    expect(sorted(Object.keys(result.checkpoints))).toEqual(sorted(AX_CHECKPOINT_KEYS));
  });

  it('names every migration path', () => {
    expect(sorted(Object.keys(messages.axDiagnosis.platforms))).toEqual(sorted(AX_PLATFORMS));
  });

  it('names every target system shown on the lead', () => {
    for (const system of TARGET_SYSTEMS) {
      expect(messages.pipeline.targetSystem).toHaveProperty(system);
    }
  });
});
