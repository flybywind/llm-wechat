// 导入所需库
import { marked } from 'marked';

class SmartMarkdownConverter {
  constructor(options = {}) {
    this.options = {
      gfm: true,
      breaks: true,
      pedantic: false,
      sanitize: true,
      smartLists: true,
      smartypants: true,
      ...options
    };

    marked.setOptions(this.options);
  }

  /**
   * 预处理Markdown文本，识别并处理代码块
   * @param {string} text Markdown文本
   * @returns {object} 处理后的文本和代码块映射
   */
  preprocessCodeBlocks(text) {
    const codeBlocks = new Map();
    let blockId = 0;
    let processedText = text;
    
    // 查找所有以```开始的位置
    const startPositions = [];
    let searchPos = 0;
    while (true) {
      const pos = processedText.indexOf('```', searchPos);
      if (pos === -1) break;
      startPositions.push(pos);
      searchPos = pos + 3;
    }

    // 如果找到开始标记
    if (startPositions.length > 0) {
      // 从后向前处理，避免位置改变影响前面的索引
      for (let i = startPositions.length - 1; i >= 0; i--) {
        const startPos = startPositions[i];
        // 查找下一个```
        const endPos = processedText.indexOf('```', startPos + 3);
        
        if (endPos !== -1) {
          // 找到配对的结束标记
          const codeBlock = processedText.substring(startPos, endPos + 3);
          const placeholder = `__CODE_BLOCK_${blockId}__`;
          codeBlocks.set(placeholder, codeBlock);
          
          // 替换代码块为占位符
          processedText = processedText.substring(0, startPos) +
                         placeholder +
                         processedText.substring(endPos + 3);
          
          blockId++;
        } else {
          // 未找到配对的结束标记，将剩余文本作为未完成的代码块处理
          const codeBlock = processedText.substring(startPos);
          const placeholder = `__INCOMPLETE_CODE_BLOCK_${blockId}__`;
          codeBlocks.set(placeholder, codeBlock);
          
          // 替换未完成的代码块为占位符
          processedText = processedText.substring(0, startPos) + placeholder;
          
          blockId++;
        }
      }
    }

    return { processedText, codeBlocks };
  }

  /**
   * 还原代码块
   * @param {string} text 处理后的文本
   * @param {Map} codeBlocks 代码块映射
   * @returns {string} 还原后的文本
   */
  restoreCodeBlocks(text, codeBlocks) {
    let restoredText = text;
    
    for (const [placeholder, codeBlock] of codeBlocks.entries()) {
      if (placeholder.includes('INCOMPLETE')) {
        // 未配对的代码块，保持原始文本
        restoredText = restoredText.replace(
          placeholder,
          `<pre>${this.escapeHtml(codeBlock)}</pre>`
        );
      } else {
        // 检查代码块是否有效
        if (this.isValidCodeBlock(codeBlock)) {
          // 有效的代码块，使用marked转换
          restoredText = restoredText.replace(
            placeholder,
            marked(codeBlock)
          );
        } else {
          // 无效的代码块，保持原始文本
          restoredText = restoredText.replace(
            placeholder,
            `<pre>${this.escapeHtml(codeBlock)}</pre>`
          );
        }
      }
    }
    
    return restoredText;
  }

  /**
   * 验证代码块语法
   * @param {string} codeBlock 代码块文本
   * @returns {boolean} 是否是有效的代码块
   */
  isValidCodeBlock(codeBlock) {
    // 检查开始和结束标记
    const lines = codeBlock.split('\n');
    const firstLine = lines[0].trim();
    const lastLine = lines[lines.length - 1].trim();

    // 确保开始和结束都是```，且中间至少有一行内容
    return firstLine.startsWith('```') && 
           lastLine === '```' && 
           lines.length > 2;
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
      ].some(pattern => pattern.test(text));

      if (hasInvalidSyntax) {
        return false;
      }

      // 检查是否包含至少一个有效的Markdown元素
      const hasValidElement = Object.values(structureChecks)
        .some(pattern => pattern.test(text));

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
    if (!text || typeof text !== 'string') {
      return '';
    }

    // 首先处理代码块
    const { processedText, codeBlocks } = this.preprocessCodeBlocks(text);

    // 将剩余文本分割成块进行处理
    const blocks = processedText.split('\n\n');
    const convertedBlocks = blocks.map(block => {
      // 如果块包含代码块占位符，保持原样
      if (Array.from(codeBlocks.keys()).some(placeholder => block.includes(placeholder))) {
        return block;
      }

      try {
        if (this.isValidMarkdown(block)) {
          return marked(block);
        } else {
          return `<pre>${this.escapeHtml(block)}</pre>`;
        }
      } catch (error) {
        return `<pre>${this.escapeHtml(block)}</pre>`;
      }
    });

    // 合并处理后的块并还原代码块
    return this.restoreCodeBlocks(convertedBlocks.join('\n'), codeBlocks);
  }

  /**
   * 转义HTML特殊字符
   * @param {string} text 需要转义的文本
   * @returns {string} 转义后的文本
   */
  escapeHtml(text) {
    const htmlEntities = {
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      '"': '&quot;',
      "'": '&#39;'
    };
    return text.replace(/[&<>"']/g, char => htmlEntities[char]);
  }
}

export default SmartMarkdownConverter;