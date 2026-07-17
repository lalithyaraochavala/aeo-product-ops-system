/**
 * The backend sometimes returns free text containing markdown-style links
 * — e.g. "[widgetco.com](https://widgetco.com)" — since that's a natural
 * format for an LLM to cite a source in. Rendered as plain text, brackets
 * and parens leak through raw. This parses that pattern and renders real
 * <a> elements instead.
 */
import type { ReactNode } from "react";

const MARKDOWN_LINK_PATTERN = /\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g;

export default function LinkedText({ text, className }: { text: string; className?: string }) {
  const nodes: ReactNode[] = [];
  let lastIndex = 0;
  let match: RegExpExecArray | null;
  let key = 0;

  MARKDOWN_LINK_PATTERN.lastIndex = 0;
  while ((match = MARKDOWN_LINK_PATTERN.exec(text)) !== null) {
    if (match.index > lastIndex) {
      nodes.push(text.slice(lastIndex, match.index));
    }
    const [, label, url] = match;
    nodes.push(
      <a
        key={key++}
        href={url}
        target="_blank"
        rel="noopener noreferrer"
        className="font-mono text-accent underline underline-offset-2 hover:opacity-80"
      >
        {label}
      </a>
    );
    lastIndex = match.index + match[0].length;
  }
  if (lastIndex < text.length) {
    nodes.push(text.slice(lastIndex));
  }

  return <span className={className}>{nodes}</span>;
}
