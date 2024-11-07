// 导入所需库
import { marked } from 'marked';
/**
 * 专门针对流式文本流的markdown转换器。通常都是在结尾处可能有不合法的markdown代码块。
 */
class SmartMarkdownConverter {
  constructor(options = {}) {
    this.options = {
      gfm: true,
      breaks: true,
      pedantic: false,
      sanitize: true,
      smartLists: true,
      smartypants: true,
      ...options,
    };
    this.valid_code_prefix = "__CODE_BLOCK_";
    this.invalid_code_prefix = "__INVALID_BLOCK_";

    marked.setOptions(this.options);
  }

  /**
   * 预处理Markdown文本，识别并处理代码块
   * 如果是合法的代码块，则直接通过markdown转换，否则保持原始文本
   * @param {string} text Markdown文本
   * @returns {object} 处理后的文本和代码块映射
   */
  preprocessCodeBlocks(text) {
    // 查找所有以```开始的位置
    const startPositions = [];
    let searchPos = 0;
    while (true) {
      const pos = text.indexOf("```", searchPos);
      if (pos === -1) break;
      startPositions.push(pos);
      searchPos = pos + 3;
    }

    if (startPositions.length % 2 == 0) {
      // 有偶数个```，可以配对，说明全是合法的代码块，直接返回
      return [text, ""];
    } else {
      // 有奇数个```，说明有未配对的代码块，将最后一个截取出来
      return [
        text.substring(0, startPositions[startPositions.length - 1]),
        text.substring(startPositions[startPositions.length - 1]),
      ];
    }
  }

  /**
   * 验证代码块语法
   * @param {string} codeBlock 代码块文本
   * @returns {boolean} 是否是有效的代码块
   */
  isValidCodeBlock(codeBlock) {
    // 检查开始和结束标记
    const lines = codeBlock.split("\n");
    const firstLine = lines[0].trim();
    const lastLine = lines[lines.length - 1].trim();

    // 确保开始和结束都是```，且中间至少有一行内容
    return firstLine.startsWith("```") && lastLine === "```" && lines.length > 2;
  }

  /**
   * 验证Markdown语法的合法性（不包括代码块）
   * @param {string} text Markdown文本
   * @returns {boolean} 是否合法
   */
  isValidMarkdown(text) {
    try {
      const structureChecks = {
        headers: /^#{1,6}\s.+$/m,
        lists: /^[-*+]\s.+$/m,
        links: /\[([^\]]+)\]\(([^)]+)\)/,
        images: /!\[([^\]]*)\]\(([^)]+)\)/,
        tables: /\|[^|]+\|/m,
      };

      // 检查是否存在明显的语法错误
      const hasInvalidSyntax = [
        /\[([^\]]*$)/, // 未闭合的链接
        /\(([^)]*$)/, // 未闭合的括号
        /\|\s*\n[^|]*$/, // 未完成的表格
      ].some((pattern) => pattern.test(text));

      if (hasInvalidSyntax) {
        return false;
      }

      // 检查是否包含至少一个有效的Markdown元素
      const hasValidElement = Object.values(structureChecks).some((pattern) => pattern.test(text));

      return hasValidElement || text.trim().length === 0;
    } catch (error) {
      return false;
    }
  }

  /**
   * 智能转换Markdown文本
   * @param {string} text Markdown文本
   * @returns {string} 转换后的HTML或原始文本
   */
  convert(text) {
    if (!text || typeof text !== "string") {
      return "";
    }

    // 首先处理代码块
    const [validText, incomplteCodeBlocks] = this.preprocessCodeBlocks(text);
    var htmlText = "";
    if (this.isValidMarkdown(validText)) {
      // 如果是合法的Markdown，直接转换
      htmlText = marked(validText);
    } else {
      htmlText = `<pre>${this.escapeHtml(validText)}</pre>`;
    }
    if (incomplteCodeBlocks.length > 0) {
      // 有未配对的代码块，直接返回
      return htmlText + `<pre>${this.escapeHtml(incomplteCodeBlocks)}</pre>`;
    } else {
      return htmlText;
    }
  }

  /**
   * 转义HTML特殊字符
   * @param {string} text 需要转义的文本
   * @returns {string} 转义后的文本
   */
  escapeHtml(text) {
    const htmlEntities = {
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      '"': "&quot;",
      "'": "&#39;",
    };
    return text.replace(/[&<>"']/g, (char) => htmlEntities[char]);
  }
}

export default SmartMarkdownConverter;