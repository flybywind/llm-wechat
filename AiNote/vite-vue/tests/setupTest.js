import { expect, vi } from "vitest";
import { config } from "@vue/test-utils";
import { config as envconf } from "dotenv";
envconf();
// Example: Mock global objects or APIs if necessary
// globalThis.document = globalThis.document || {};

// Add your custom configurations
// config.global.mocks = {
//   $t: (msg) => msg, // i18n example
// };
// If specific browser APIs like window or document are missing, add mocks to global:
// vi.stubGlobal("document", {
//   createElement: vi.fn(),
// });
// demo of vue test
// // Configure.test.js
// import { describe, it, expect } from "vitest";
// import { mount } from "@vue/test-utils";
// import Configure from "../src/components/Configure.vue";

// describe("Configure", () => {
//   const baseSchema = {
//     type: "object",
//     repr_name: "llm_test",
//     properties: {
//       selections: {
//         type: "array",
//         items: { enum: ["llm1", "llm2"] },
//         default: "llm1",
//       },
//       llm: {
//         type: "object",
//         repr_name: "llm",
//         properties: {
//           top_p: { type: "number", default: 0.9 },
//         },
//       },
//     },
//   };
//   it("renders object properties", () => {
//     const wrapper = mount(Configure, {
//       props: { schema: baseSchema },
//     });
//     console.log("html content:", wrapper.html());
//     expect(wrapper.find(".recursive-form")).toBeTruthy();
//     expect(wrapper.findAll("details")).toHaveLength(2);
//     expect(wrapper.findAll("summary")).toHaveLength(2);
//     expect(wrapper.find("select")).toBeTruthy();
//     expect(wrapper.find('input[type="number"]')).toBeTruthy();

//     expect(wrapper.findAll('input[type="number"]')).toHaveLength(1);
//     expect(wrapper.findAll("details summary")).toHaveLength(2);
//     expect(wrapper.findAll("details div details summary")).toHaveLength(1);
//   });

//   it("emits update:schema event when input changes", async () => {
//     const wrapper = mount(Configure, {
//       props: { schema: baseSchema },
//     });

//     // Find and update the number input
//     const numberInput = wrapper.find('input[type="number"]');
//     await numberInput.setValue("1.0");

//     // Verify emission
//     const emittedSchema = wrapper.emitted("update:schema");
//     expect(emittedSchema).toBeTruthy();
//     expect(emittedSchema[0][0].properties.llm.properties.top_p.default).toBe(1.0);
//   });

//   it("handles array type selection changes", async () => {
//     const wrapper = mount(Configure, {
//       props: { schema: baseSchema },
//     });

//     // Find and update the select
//     const select = wrapper.find("select");
//     await select.setValue("llm2");

//     // Verify emission
//     expect(wrapper.emitted("update:schema")).toBeTruthy();
//     const emittedSchema = wrapper.emitted("update:schema")[0][0];
//     expect(emittedSchema.properties.selections.default).toBe("llm2");
//   });

//   it("maintains schema structure after updates", async () => {
//     const wrapper = mount(Configure, {
//       props: { schema: baseSchema },
//     });

//     // Make multiple changes
//     const numberInput = wrapper.find('input[type="number"]');
//     await numberInput.setValue("1.0");

//     const select = wrapper.find("select");
//     await select.setValue("llm2");

//     // Verify final schema structure
//     const finalEmission = wrapper.emitted("update:schema").pop()[0];
//     expect(finalEmission).toMatchObject({
//       type: "object",
//       repr_name: "llm_test",
//       properties: {
//         selections: {
//           type: "array",
//           items: { enum: ["llm1", "llm2"] },
//           default: "llm2",
//         },
//         llm: {
//           type: "object",
//           repr_name: "llm",
//           properties: {
//             top_p: { type: "number", default: 1.0 },
//           },
//         },
//       },
//     });
//   });
// });
