import { describe, it, expect, test } from "vitest";
import SmartMarkdownConverter from "../src/utils/smart_markdown";

// 测试用例
const testCases = [
  // 测试用例1：正常的代码块
  {
    input: `# 标题
这是一些正常文本。

\`\`\`javascript
function hello() {
  console.log("Hello World!");
}
\`\`\`

这是更多文本。`,
    expectOut: `<h1>标题</h1>
<p>这是一些正常文本。</p>
<pre><code class="language-javascript">function hello() {
  console.log(&quot;Hello World!&quot;);
}
</code></pre>
<p>这是更多文本。</p>
`,
  },
  // case2
  {
    input: `# 未配对代码块测试
这是一些文本

\`\`\`python
def incomplete_function():
    print("This is incomplete")
    
更多文本在这里。`,
    expectOut: `<h1>未配对代码块测试</h1>
<p>这是一些文本</p>
<pre>\`\`\`python
def incomplete_function():
    print(&quot;This is incomplete&quot;)
    
更多文本在这里。</pre>`,
  },

  // 测试用例3：多个代码块，包括配对和未配对
  {
    input: `# 混合代码块测试
\`\`\`javascript
// 这是完整的代码块
console.log("complete");
\`\`\`

正常文本

\`\`\`python
# 这是未配对的代码块
print("incomplete")

更多文本...`,
    expectOut: `<h1>混合代码块测试</h1>
<pre><code class="language-javascript">// 这是完整的代码块
console.log(&quot;complete&quot;);
</code></pre>
<p>正常文本</p>
<pre>\`\`\`python
# 这是未配对的代码块
print(&quot;incomplete&quot;)

更多文本...</pre>`,
  },
  ,
  // 测试用例4：空代码块
  {
    input: `# 空代码块测试
\`\`\`
\`\`\`

正常文本`,
    expectOut: `<h1>空代码块测试</h1>
<pre><code>
</code></pre>
<p>正常文本</p>
`,
  },

  // 测试用例5：只有开始标记的空代码块
  {
    input: `# 未配对的空代码块测试
\`\`\`

正常文本`,
    expectOut: `<h1>未配对的空代码块测试</h1>
<pre>\`\`\`

正常文本</pre>`,
  },
];

// 运行测试
const converter = new SmartMarkdownConverter();

describe("SmartMarkdownConverter", () => {
  testCases.forEach(({ input, expectOut }, index) => {
    test(`测试用例 ${index + 1}`, () => {
      const actualOut = converter.convert(input);
      expect(actualOut).toBe(expectOut);
    });
  });
});
