import { describe, it, expect } from 'vitest';
import { calculateEntropy, generateDNASequence, seededRandom } from './entropy';

describe('entropy utilities', () => {
  it('should calculate shannon entropy correctly', () => {
    expect(calculateEntropy('AAAA')).toBe(0);
    expect(calculateEntropy('ACGT')).toBe(2);
  });

  it('should generate deterministic random values', () => {
    const rng1 = seededRandom(123);
    const rng2 = seededRandom(123);
    expect(rng1()).toBe(rng2());
    expect(rng1()).toBe(rng2());
  });

  it('should generate deterministic DNA sequences', () => {
    const seq1 = generateDNASequence(10, 42);
    const seq2 = generateDNASequence(10, 42);
    const seq3 = generateDNASequence(10, 99);
    expect(seq1).toBe(seq2);
    expect(seq1).not.toBe(seq3);
    expect(seq1).toMatch(/^[ACGT]+$/);
  });
});
