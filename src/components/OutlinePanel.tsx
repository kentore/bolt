
import React from 'react';
import { Hash, FileText, ChevronRight, ChevronDown } from 'lucide-react';
import { Card } from '@/components/ui/card';
import { Checkbox } from '@/components/ui/checkbox';

interface TextElement {
  id: string;
  text: string;
  isTitle: boolean;
  number?: number;
  titleNumber?: number;
  visible: boolean;
}

interface OutlinePanelProps {
  textBlocks: TextElement[];
  onScrollToBlock: (blockId: string) => void;
  collapsedTitles: Set<string>;
}

const OutlinePanel: React.FC<OutlinePanelProps> = ({ 
  textBlocks, 
  onScrollToBlock, 
  collapsedTitles 
}) => {
  const getAssociatedParagraphs = (titleIndex: number) => {
    const paragraphs = [];
    for (let i = titleIndex + 1; i < textBlocks.length; i++) {
      if (textBlocks[i].isTitle) break;
      paragraphs.push(textBlocks[i]);
    }
    return paragraphs;
  };

  const renderOutlineItems = () => {
    const items = [];
    let currentTitleIndex = -1;

    textBlocks.forEach((block, index) => {
      if (block.isTitle) {
        currentTitleIndex = index;
        const isCollapsed = collapsedTitles.has(block.id);
        const associatedParagraphs = getAssociatedParagraphs(index);
        
        items.push(
          <div key={block.id} className="mb-2">
            {/* Title Item */}
            <div
              className="flex items-center gap-2 p-2 rounded-md hover:bg-blue-100 cursor-pointer transition-colors"
              onClick={() => onScrollToBlock(block.id)}
            >
              <div className="flex items-center gap-1">
                {isCollapsed ? (
                  <ChevronRight className="w-3 h-3 text-amber-600" />
                ) : (
                  <ChevronDown className="w-3 h-3 text-amber-600" />
                )}
                <Hash className="w-4 h-4 text-amber-600" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="font-semibold text-sm text-amber-800 truncate">
                  Título {block.titleNumber}
                </div>
                <div className="text-xs text-amber-600 truncate">
                  {block.text.slice(0, 40)}{block.text.length > 40 ? '...' : ''}
                </div>
              </div>
            </div>

            {/* Associated Paragraphs (only show if not collapsed) */}
            {!isCollapsed && associatedParagraphs.map((paragraph) => (
              <div
                key={paragraph.id}
                className="ml-6 flex items-center gap-2 p-1 rounded-md hover:bg-blue-50 cursor-pointer transition-colors"
                onClick={() => onScrollToBlock(paragraph.id)}
              >
                <Checkbox className="flex-shrink-0" />
                <FileText className="w-3 h-3 text-blue-600" />
                <div className="flex-1 min-w-0">
                  <div className="text-xs text-blue-700">
                    Párrafo {paragraph.number} ({paragraph.text.length} caracteres)
                  </div>
                </div>
              </div>
            ))}
          </div>
        );
      } else if (currentTitleIndex === -1) {
        // Standalone paragraph (not under any title)
        items.push(
          <div
            key={block.id}
            className="flex items-center gap-2 p-2 rounded-md hover:bg-blue-50 cursor-pointer transition-colors mb-1"
            onClick={() => onScrollToBlock(block.id)}
          >
            <Checkbox className="flex-shrink-0" />
            <FileText className="w-4 h-4 text-blue-600" />
            <div className="flex-1 min-w-0">
              <div className="text-sm text-blue-700">
                Párrafo {block.number}
              </div>
              <div className="text-xs text-blue-500">
                {block.text.length} caracteres
              </div>
            </div>
          </div>
        );
      }
    });

    return items;
  };

  return (
    <Card className="h-full p-4 shadow-lg border-0 bg-white/90 backdrop-blur-sm">
      <div className="flex items-center gap-2 mb-4">
        <Hash className="w-5 h-5 text-gray-700" />
        <h2 className="text-lg font-semibold text-gray-800">Vista General</h2>
      </div>
      
      <div className="space-y-1 max-h-[calc(100vh-200px)] overflow-y-auto pr-2">
        {textBlocks.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <Hash className="w-8 h-8 mx-auto mb-2 opacity-50" />
            <p className="text-sm">Sin contenido</p>
          </div>
        ) : (
          renderOutlineItems()
        )}
      </div>
    </Card>
  );
};

export default OutlinePanel;
