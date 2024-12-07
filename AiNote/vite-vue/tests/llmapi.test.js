import { test, expect, describe, it } from "vitest";

import { QianwenApi, Message, Role } from "../src/utils/llmapi";
describe("Qianwen test", () => {
  const apiKey = process.env.QIANWEN_API_KEY;
  const qianWenModel = "qwen-plus";
  it("should return a valid response from chat", async () => {
    console.log("apiKey:", apiKey);
    const qianwen = new QianwenApi(apiKey, qianWenModel, { stream: false });
    qianwen.setSystem(
      "你是一个Ai机器人，在回答问题之前，请首先分析一下可能的上下文，并结合之前的提问，找出问题的关键，并给出一个简短的回答。"
    );
    expect(qianwen.params.top_p).toBe(0.8);
    expect(qianwen.params.stream).toBe(false);
    const response = await qianwen.chat(Role.User, "鸣人最拿手的忍术是什么？");
    expect(response).toHaveProperty("choices");
    expect(response.choices[0].message).toHaveProperty("role", "assistant");
    expect(response.choices[0].message).toHaveProperty("content");
    // p.then((response) => {
    //   console.log(response);
    //   expect(response).toBeDefined();
    // });
  });
  it("should emit data events for each stream chunk", async () => {
    // const mockStreamData = [
    //   '{"choices":[{"message":{"role":"ai","content":"Hello"}}]}\n',
    //   '{"choices":[{"message":{"role":"ai","content":" world"}}]}\n',
    // ];

    // // Mock fetch to return a simulated stream response
    // const mockFetch = vi.fn().mockImplementation(() => {
    //   const stream = new ReadableStream({
    //     start(controller) {
    //       mockStreamData.forEach((chunk) => {
    //         controller.enqueue(new TextEncoder().encode(chunk));
    //       });
    //       controller.close();
    //     },
    //   });

    //   return Promise.resolve({
    //     body: stream,
    //     ok: true,
    //     status: 200,
    //   });
    // });

    // global.fetch = mockFetch;

    const qianwen = new QianwenApi(apiKey, qianWenModel, { stream: true });
    qianwen.setSystem("You are a helpful assistant.");

    const stream = await qianwen.chat(Role.User, "Hello, how are you?");
    const results = [];
    await new Promise((resolve, reject) => {
      stream.on("data", (data) => {
        console.log("data:", data);
        results.push(data);
      });

      stream.on("end", () => {
        console.log("end");
        resolve();
      });

      stream.on("error", (error) => {
        console.error(error);
        reject(error);
      });
    });
    expect(results.length).toBeGreaterThan(0);
  });

});
