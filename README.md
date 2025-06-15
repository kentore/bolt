# Block Flow Editor Plus

A modern web-based text block editor built with React and TypeScript. This application allows users to import text, break it down into manageable blocks (titles and paragraphs), edit these blocks, and navigate the document structure with an intuitive interface.

## Features

- Import text by typing, pasting, or opening `.txt` files
- Automatically analyze text to identify titles and paragraphs
- Edit, delete, and add text blocks with real-time updates
- Toggle block type between title and paragraph
- Collapse and expand titles to manage content visibility
- Navigate document structure using an interactive outline panel
- Save the edited blocks to a `.txt` file
- View comprehensive statistics about the text (word count, block counts)
- "Clear All" functionality to reset the editor
- Responsive design that works on desktop and mobile

## Tech Stack

- React 18 with TypeScript
- Vite for fast development and building
- Tailwind CSS for styling
- shadcn/ui components for consistent UI
- Lucide React for icons
- React Router for navigation

## Getting Started

1. Clone this repository
2. Install dependencies:
   \`\`\`bash
   npm install
   \`\`\`
3. Start the development server:
   \`\`\`bash
   npm run dev
   \`\`\`
4. Open your browser and navigate to `http://localhost:5173`

## Build for Production

\`\`\`bash
npm run build
\`\`\`

The built files will be in the `dist` directory.
