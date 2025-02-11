import {
  FaHeading,
  FaListUl,
  FaListOl,
  FaQuoteRight,
  FaCode,
  FaImage,
  FaLink,
} from "react-icons/fa";

export const BLOCK_CONTENTS: Record<string, string> = {
  heading1: "# REPLACE ME",
  heading2: "## REPLACE ME",
  heading3: "### REPLACE ME",
  "unordered-list": " REPLACE ME",
  "ordered-list": "REPLACE ME",
  blockquote: "REPLACE ME",
  code: "REPLACE ME",
  image: "REPLACE ME",
  link: "REPLACE ME",
};

export interface BlockContent {
  id: string;
  content: string;
}

export const BLOCKS = [
  {
    id: "heading1",
    category: "Headers",
    label: "Heading 1",
    icon: FaHeading,
    content: BLOCK_CONTENTS.heading1,
  },
  {
    id: "heading2",
    category: "Headers",
    label: "Heading 2",
    icon: FaHeading,
    content: BLOCK_CONTENTS.heading2,
  },
  {
    id: "heading3",
    category: "Headers",
    label: "Heading 3",
    icon: FaHeading,
    content: BLOCK_CONTENTS.heading3,
  },
  {
    id: "unordered_list",
    category: "Lists",
    label: "Unordered List",
    icon: FaListUl,
    content: BLOCK_CONTENTS["unordered-list"],
  },
  {
    id: "ordered_list",
    category: "Lists",
    label: "Ordered List",
    icon: FaListOl,
    content: BLOCK_CONTENTS["ordered-list"],
  },
  {
    id: "blockquote",
    category: "Blockquotes",
    label: "Blockquote",
    icon: FaQuoteRight,
    content: BLOCK_CONTENTS.blockquote,
  },
  {
    id: "code",
    category: "Code",
    label: "Code Block",
    icon: FaCode,
    content: BLOCK_CONTENTS.code,
  },
  {
    id: "image",
    category: "Media",
    label: "Image",
    icon: FaImage,
    content: BLOCK_CONTENTS.image,
  },
  {
    id: "link",
    category: "Media",
    label: "Link",
    icon: FaLink,
    content: BLOCK_CONTENTS.link,
  },
];

export const CATEGORIES = Array.from(
  new Set(BLOCKS.map((block) => block.category)),
);

export const parseMarkdownToBlocks = (markdown: string): BlockContent[] => {
  const lines = markdown.split("\n\n").filter(Boolean);

  return lines.map((content) => {
    // Match content with block types
    const matchBlock = BLOCKS.find((block) => {
      switch (block.id) {
        case "heading1":
          return content.startsWith("# ");
        case "heading2":
          return content.startsWith("## ");
        case "heading3":
          return content.startsWith("### ");
        case "unordered_list":
          return content.split("\n").every((line) => line.startsWith("- "));
        case "ordered_list":
          return content.split("\n").every((line) => /^\d+\.\s/.test(line));
        case "blockquote":
          return content.split("\n").every((line) => line.startsWith("> "));
        case "code":
          return content.startsWith("```") && content.endsWith("```");
        case "image":
          return content.startsWith("![");
        case "link":
          return content.startsWith("[");
        default:
          return false;
      }
    });

    // Clean content based on block type
    const cleanContent = matchBlock
      ? (() => {
          switch (matchBlock.id) {
            case "heading1":
              return content.replace(/^#\s/, "");
            case "heading2":
              return content.replace(/^##\s/, "");
            case "heading3":
              return content.replace(/^###\s/, "");
            case "unordered_list":
              return content
                .split("\n")
                .map((line) => line.replace(/^-\s/, ""))
                .join("\n");
            case "ordered_list":
              return content
                .split("\n")
                .map((line) => line.replace(/^\d+\.\s/, ""))
                .join("\n");
            case "blockquote":
              return content
                .split("\n")
                .map((line) => line.replace(/^>\s/, ""))
                .join("\n");
            case "code":
              return content.replace(/^```\n/, "").replace(/\n```$/, "");
            case "image":
              return content.match(/!\[(.*?)\]/)?.[1] || "";
            case "link":
              return content.match(/\[(.*?)\]/)?.[1] || "";
            default:
              return content;
          }
        })()
      : content;

    return {
      id: `${matchBlock?.id || "paragraph"}-${Date.now()}`,
      content: cleanContent,
    };
  });
};
