/**
 * Utility for generating deterministic pseudo-random sequences and calculating entropy.
 */

// Simple seeded random number generator (Linear Congruential Generator)
export function seededRandom(seed: number) {
  let s = seed;
  return function() {
    s = (s * 9301 + 49297) % 233280;
    return s / 233280;
  };
}

// Calculate Shannon entropy of a string
export function calculateEntropy(str: string): number {
  if (!str || str.length === 0) return 0;
  const len = str.length;
  const frequencies: Record<string, number> = {};
  for (let i = 0; i < len; i++) {
    const char = str[i];
    frequencies[char] = (frequencies[char] || 0) + 1;
  }
  let sum = 0;
  for (const char in frequencies) {
    const p = frequencies[char] / len;
    sum -= p * Math.log2(p);
  }
  return sum;
}

// Generate a random DNA sequence of given length deterministically from a seed
export function generateDNASequence(length: number, seed: number = 42): string {
  const chars = ['A', 'C', 'G', 'T'];
  const rng = seededRandom(seed);
  let res = '';
  for (let i = 0; i < length; i++) {
    res += chars[Math.floor(rng() * chars.length)];
  }
  return res;
}
