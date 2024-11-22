// SchemaLoader.test.js
import { describe, it, expect, vi, beforeEach } from "vitest";
import { mount, flushPromises } from "@vue/test-utils";
import ConfLoader from "../src/components/ConfiguerLoader.vue";

// Mock sample schema
const sampleSchema = {
  type: "object",
  repr_name: "test_schema",
  properties: {
    name: { type: "string", default: "" },
    age: { type: "number", default: 0 },
  },
};

// Mock fetch globally
global.fetch = vi.fn();

describe("SchemaLoader", () => {
  beforeEach(() => {
    // Clear all mocks before each test
    vi.clearAllMocks();

    // Reset fetch mock
    fetch.mockReset();
  });

  it("shows loading state initially", () => {
    // Mock successful fetch but don't resolve yet
    fetch.mockImplementationOnce(() => new Promise(() => {}));

    const wrapper = mount(ConfLoader);
    expect(wrapper.find(".loading-state").exists()).toBe(true);
    expect(wrapper.find(".loading-spinner").exists()).toBe(true);
  });

  it("loads and displays schema successfully", async () => {
    // Mock successful fetch
    fetch.mockImplementationOnce(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve(sampleSchema),
      })
    );

    const wrapper = mount(ConfLoader);

    // Wait for async operations to complete
    await flushPromises();

    // Should no longer show loading state
    expect(wrapper.find(".loading-state").exists()).toBe(false);

    // Should mount Configure component
    expect(wrapper.findComponent({ name: "Configure" }).exists()).toBe(true);
  });

  it("shows error state when fetch fails", async () => {
    // Mock failed fetch
    fetch.mockImplementationOnce(() =>
      Promise.resolve({
        ok: false,
        status: 500,
      })
    );

    const wrapper = mount(ConfLoader);

    // Wait for async operations to complete
    await flushPromises();

    // Should show error state
    expect(wrapper.find(".error-state").exists()).toBe(true);
    expect(wrapper.find(".error-message").text()).toContain("Failed to load schema");
  });

  it("retries loading when retry button is clicked", async () => {
    // First fetch fails
    fetch.mockImplementationOnce(() =>
      Promise.resolve({
        ok: false,
        status: 500,
      })
    );

    const wrapper = mount(ConfLoader);
    await flushPromises();

    // Mock successful fetch for retry
    fetch.mockImplementationOnce(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve(sampleSchema),
      })
    );

    // Click retry button
    await wrapper.find(".retry-button").trigger("click");
    await flushPromises();

    // Should now show Configure component
    expect(wrapper.findComponent({ name: "Configure" }).exists()).toBe(true);
  });

  it("handles schema updates", async () => {
    // Mock initial load
    fetch.mockImplementationOnce(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve(sampleSchema),
      })
    );

    const wrapper = mount(ConfLoader);
    await flushPromises();

    // Mock successful schema update
    fetch.mockImplementationOnce(() =>
      Promise.resolve({
        ok: true,
      })
    );

    const updatedSchema = {
      ...sampleSchema,
      properties: {
        ...sampleSchema.properties,
        age: { type: "number", default: 25 },
      },
    };

    // Trigger schema update
    await wrapper.findComponent({ name: "Configure" }).vm.$emit("update:schema", updatedSchema);
    await flushPromises();

    // Verify the POST request was made
    expect(fetch).toHaveBeenCalledWith("/api/schema", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(updatedSchema),
    });
  });
});
