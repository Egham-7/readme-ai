import {
  FaHeading,
  FaListUl,
  FaListOl,
  FaQuoteRight,
  FaCode,
  FaImage,
  FaLink,
} from "react-icons/fa";

export const BLOCK_CONTENTS: { [key: string]: string } = {
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
