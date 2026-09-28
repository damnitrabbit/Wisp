import { PSEUDONYM_RE } from '@wisp/shared';
import { randomInt } from 'node:crypto';

const ADJ = [
  'quiet', 'velvet', 'hollow', 'sleepy', 'lucky', 'misty', 'rusty', 'silver', 'gentle', 'wild',
  'shy', 'brave', 'lazy', 'swift', 'dusty', 'mellow', 'cosmic', 'fuzzy', 'salty', 'sunny',
  'moody', 'witty', 'lunar', 'amber', 'frosty', 'stormy', 'calm', 'odd', 'tiny', 'lost',
  'humble', 'clever', 'drowsy', 'fading', 'hidden', 'lonely', 'nimble', 'polite', 'rapid', 'soft'
];
const ANIMAL = [
  'otter', 'fox', 'owl', 'moth', 'heron', 'badger', 'lynx', 'crow', 'panda', 'gecko',
  'koala', 'raven', 'seal', 'wolf', 'hare', 'finch', 'yak', 'newt', 'lemur', 'bison',
  'squid', 'tapir', 'mole', 'wren', 'crane', 'ibis', 'orca', 'sloth', 'mink', 'stoat',
  'marten', 'robin', 'toad', 'eel', 'puffin', 'quail', 'dingo', 'gibbon', 'okapi', 'vole'
];

const pick = (arr) => arr[randomInt(arr.length)];

export function makeName(taken) {
  for (let i = 0; i < 50; i++) {
    const n = `${pick(ADJ)}_${pick(ANIMAL)}_${String(randomInt(100)).padStart(2, '0')}`;
    if (!taken.has(n)) return n;
  }
  // 64,000 combinations; if we're here the server is very busy. Widen the number.
  return `${pick(ADJ)}_${pick(ANIMAL)}_${String(randomInt(100)).padStart(2, '0')}`;
}

// A remembered name is only accepted if it could have come from our own word lists,
// so nobody can pick an offensive name by editing localStorage.
const ADJ_SET = new Set(ADJ);
const ANIMAL_SET = new Set(ANIMAL);
export function isValidName(n) {
  if (typeof n !== 'string' || !PSEUDONYM_RE.test(n)) return false;
  const [a, b] = n.split('_');
  return ADJ_SET.has(a) && ANIMAL_SET.has(b);
}
