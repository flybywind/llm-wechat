// RecursiveForm.spec.js
import { describe, it, expect } from "vitest";
import { mount } from "@vue/test-utils";
import Configure from "../src/components/Configure.vue";

describe("Configure", () => {
  it("renders object properties", () => {
    const schema = {
      type: "object",
      repr_name: "llm_test",
      properties: {
        selections: {
          type: "array",
          items: { enum: ["llm1", "llm2"] },
          default: "llm1",
        },
        llm: {
          type: "object",
          repr_name: "llm",
          properties: {
            top_p: { type: "number", default: 0.9 },
          },
        },
      },
    };
    const wrapper = mount(Configure, {
      props: { schema },
    });

    expect(wrapper.findAll('input[type="text"]')).toHaveLength(1);
    expect(wrapper.findAll('input[type="number"]')).toHaveLength(1);
  });

  it("emits update:schema event", async () => {
    const schema = {
      type: "object",
      properties: {
        name: { type: "string", default: "" },
      },
    };
    const wrapper = mount(Configure, {
      props: { schema },
    });

    await wrapper.find('input[type="text"]').setValue("John");
    expect(wrapper.emitted("update:schema")[0][0]).toEqual({
      type: "object",
      properties: {
        name: { type: "string", default: "John" },
      },
    });
  });

  // Add more test cases...
});
