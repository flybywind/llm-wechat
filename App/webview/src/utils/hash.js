function fnv1a(str) {
  let hash = 2166136261;
  const prime = 16777619;

  for (let i = 0; i < str.length; i++) {
    hash ^= str.charCodeAt(i);
    hash *= prime;
    hash &= 0xffffffff; // Ensure it's a 32-bit integer
  }

  return hash >>> 0;
}

export default fnv1a;
