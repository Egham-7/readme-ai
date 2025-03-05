import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { vscDarkPlus } from "react-syntax-highlighter/dist/esm/styles/prism";
import rehypeRaw from "rehype-raw";

const MarkdownPreview = ({
  content,
}: {
  content: string;
  onChange?: (value: string) => void;
}) => (
  <ReactMarkdown
    remarkPlugins={[remarkGfm]}
    rehypePlugins={[rehypeRaw]}
    className="markdown-body"
    components={{
      h1: ({ children }) => (
        <h1 className="text-3xl font-bold mb-4 pb-2 border-b">{children}</h1>
      ),
      h2: ({ children }) => (
        <h2 className="text-2xl font-semibold mt-6 mb-4">{children}</h2>
      ),
      h3: ({ children }) => (
        <h3 className="text-xl font-semibold mt-5 mb-3">{children}</h3>
      ),
      p: ({ children }) => <p className="mb-4 leading-relaxed">{children}</p>,
      ul: ({ children }) => <ul className="list-disc pl-6 mb-4">{children}</ul>,
      ol: ({ children }) => (
        <ol className="list-decimal pl-6 mb-4">{children}</ol>
      ),
      li: ({ children }) => <li className="mb-1">{children}</li>,
      a: ({ href, children }) => (
        <a href={href} className="text-blue-500 hover:underline">
          {children}
        </a>
      ),
      blockquote: ({ children }) => (
        <blockquote className="border-l-4 border-gray-200 pl-4 my-4 italic">
          {children}
        </blockquote>
      ),
      code({ className, children }) {
        const match = /language-(\w+)/.exec(className || "");
        return match ? (
          <div className="my-4">
            <SyntaxHighlighter
              style={vscDarkPlus}
              language={match[1]}
              PreTag="div"
              showLineNumbers
              wrapLines
              wrapLongLines
              customStyle={{
                margin: 0,
                borderRadius: "6px",
                fontSize: "0.9em",
              }}
            >
              {String(children)}
            </SyntaxHighlighter>
          </div>
        ) : (
          <code className="bg-gray-100 dark:bg-gray-800 px-1.5 py-0.5 rounded-md text-sm">
            {children}
          </code>
        );
      },
      table: ({ children }) => (
        <div className="overflow-x-auto my-4">
          <table className="min-w-full border border-gray-200 dark:border-gray-700">
            {children}
          </table>
        </div>
      ),
      th: ({ children }) => (
        <th className="border border-gray-200 dark:border-gray-700 px-4 py-2 bg-gray-50 dark:bg-gray-800">
          {children}
        </th>
      ),
      td: ({ children }) => (
        <td className="border border-gray-200 dark:border-gray-700 px-4 py-2">
          {children}
        </td>
      ),
    }}
  >
    {content}
  </ReactMarkdown>
);

export default MarkdownPreview;
