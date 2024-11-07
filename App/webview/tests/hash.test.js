import { test, expect } from "vitest";
import fnv1a from "../src/utils/hash";

test("fnv1a", () => {
  const testCases = [
    {
      input: "Hello World!",
      expectOut: 1411507076,
    },
    {
      input: "2Hello World",
      expectOut: 2920863832,
    },
    {
      input: "ello World!!",
      expectOut: 3136027550,
    },
  ];
  testCases.forEach((element) => {
    expect(fnv1a(element.input)).toBe(element.expectOut);
  });
  // expect(fnv1a("Hello World!")).toBe(1411507076);
  // expect(fnv1a("2Hello World")).toBe(0x6a396f07);
  // expect(fnv1a("ello World!!")).toBe(0x6a396f09);
});
