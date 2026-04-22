import { marked } from 'marked';
import { markedHighlight } from 'marked-highlight';
import hljs from 'highlight.js';
import markedKatex from 'marked-katex-extension';

marked.use(
  markedHighlight({
    langPrefix: 'hljs language-',
    highlight(code, lang) {
      return hljs.highlightAuto(code).value;
    },
  }),
  markedKatex(),
);

const result = marked.parse('# Hello\n```js\nconst x = 1;\n```');
console.log('Result type:', typeof result);
console.log('Result is promise:', result instanceof Promise);
