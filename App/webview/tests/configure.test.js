// Configure.test.js
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
    console.log("html content:", wrapper.html());
    expect(wrapper.findAll('input[type="text"]')).toHaveLength(1);
    expect(wrapper.findAll("details summary")).toHaveLength(2);
    expect(wrapper.findAll("details div details summary")).toHaveLength(1);
  });

  it("emits update:schema event", async () => {
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

    await wrapper.find('input[type="text"]').setValue(1.0);
    let emitted = wrapper.emitted("update:schema");
    console.log("emitted:", emitted); // why is this undefined?
    expect(wrapper.emitted("update:schema")[0][0]).toEqual({
      type: "object",
      properties: {
        name: { type: "number", default: 1.0 },
      },
    });
    await wrapper.find("selection").setValue("llm2");
    expect(wrapper.emitted("update:schema")[0][0]).toEqual({
      type: "object",
      properties: {
        name: { type: "number", default: 1.0 },
      },
    });
  });

  // Add more test cases...
});
