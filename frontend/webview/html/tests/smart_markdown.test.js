import { describe, it, expect, test } from "vitest";
import SmartMarkdownConverter from "../src/utils/smart_markdown";

// 测试用例
const testCases = [
  // 测试用例1：正常的代码块
  `# 标题
这是一些正常文本。

\`\`\`javascript
function hello() {
  console.log("Hello World!");
}
\`\`\`

这是更多文本。`,

  // 测试用例2：未配对的代码块
  `# 未配对代码块测试
这是一些文本

\`\`\`python
def incomplete_function():
    print("This is incomplete")
    
更多文本在这里。`,

  // 测试用例3：多个代码块，包括配对和未配对
  `# 混合代码块测试
\`\`\`javascript
// 这是完整的代码块
console.log("complete");
\`\`\`

正常文本

\`\`\`python
# 这是未配对的代码块
print("incomplete")

更多文本...`,

  // 测试用例4：空代码块
  `# 空代码块测试
\`\`\`
\`\`\`

正常文本`,

  // 测试用例5：只有开始标记的空代码块
  `# 未配对的空代码块测试
\`\`\`

正常文本`,
];

// 运行测试
const converter = new SmartMarkdownConverter();

describe("SmartMarkdownConverter", () => {
  testCases.forEach((htmlText, index) => {
    test(`测试用例 ${index + 1}`, () => {
      console.log(`\n测试用例 ${index + 1}:`);
      console.log("输入:\n", htmlText);
      console.log("输出:\n", converter.convert(htmlText));
      console.log(`==== 测试用例 ${index + 1} 结束 ====\n`);
    });
  });
});
