import { test, expect, describe, it } from "vitest";

import { QianwenApi, Message, Role } from "../src/utils/llmapi";
describe("Qianwen test", () => {
  const apiKey = process.env.QIANWEN_API_KEY;
  it("should return a valid response from chat", async () => {
    console.log("apiKey:", apiKey);
    const qianwen = new QianwenApi(apiKey, "qwen-plus", { stream: false });
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
});
