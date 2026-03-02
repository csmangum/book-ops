import Markdown from "react-markdown";

export function MarkdownViewer({ markdown }: { markdown: string }) {
  return (
    <article className="prose prose-zinc dark:prose-invert max-w-none">
      <Markdown>{markdown}</Markdown>
    </article>
  );
}
