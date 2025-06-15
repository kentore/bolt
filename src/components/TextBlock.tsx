
import React, { useState, useEffect, useRef } from 'react';
import { ChevronDown, ChevronRight, Trash2, Hash } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Card } from '@/components/ui/card';

interface TextElement {
  id: string;
  text: string;
  isTitle: boolean;
  number?: number;
  titleNumber?: number;
  visible: boolean;
}

interface TextBlockProps {
  block: TextElement;
  onUpdateText: (id: string, text: string) => void;
  onDelete: (id: string) => void;
  onToggleCollapse: (titleId: string, collapsed: boolean) => void;
  textBlocks: TextElement[];
}

const TextBlock: React.FC<TextBlockProps> = ({
  block,
  onUpdateText,
  onDelete,
  onToggleCollapse,
  textBlocks
}) => {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [localText, setLocalText] = useState(block.text);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    setLocalText(block.text);
  }, [block.text]);

  useEffect(() => {
    adjustTextareaHeight();
  }, [localText]);

  const adjustTextareaHeight = () => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      const newHeight = Math.max(60, Math.min(textarea.scrollHeight + 4, 200));
      textarea.style.height = `${newHeight}px`;
    }
  };

  const handleTextChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newText = e.target.value;
    setLocalText(newText);
    onUpdateText(block.id, newText);
  };

  const handleToggleCollapse = () => {
    if (block.isTitle) {
      const newCollapsed = !isCollapsed;
      setIsCollapsed(newCollapsed);
      onToggleCollapse(block.id, newCollapsed);
    }
  };

  const getAssociatedParagraphsStats = () => {
    if (!block.isTitle) return null;

    const blockIndex = textBlocks.findIndex(b => b.id === block.id);
    if (blockIndex === -1) return null;

    const associatedParagraphs = [];
    for (let i = blockIndex + 1; i < textBlocks.length; i++) {
      if (textBlocks[i].isTitle) break;
      associatedParagraphs.push(textBlocks[i]);
    }

    const totalWords = associatedParagraphs.reduce((sum, p) => {
      return sum + (p.text.trim() ? p.text.trim().split(/\s+/).length : 0);
    }, 0);

    const totalChars = associatedParagraphs.reduce((sum, p) => sum + p.text.length, 0);

    return {
      count: associatedParagraphs.length,
      words: totalWords,
      chars: totalChars
    };
  };

  const getWordCount = () => {
    return localText.trim() ? localText.trim().split(/\s+/).length : 0;
  };

  const getCharCount = () => {
    return localText.length;
  };

  const associatedStats = getAssociatedParagraphsStats();

  return (
    <Card className={`transition-all duration-200 hover:shadow-md ${
      block.isTitle 
        ? 'border-l-4 border-l-amber-400 bg-gradient-to-r from-amber-50 to-orange-50' 
        : 'border-l-4 border-l-blue-400 bg-gradient-to-r from-blue-50 to-indigo-50'
    }`}>
      {/* Header */}
      <div className={`flex items-center justify-between p-3 rounded-t-lg ${
        block.isTitle ? 'bg-amber-100 border-b border-amber-200' : 'bg-blue-100 border-b border-blue-200'
      }`}>
        <div className="flex items-center gap-2">
          {block.isTitle && (
            <Button
              variant="ghost"
              size="sm"
              onClick={handleToggleCollapse}
              className="p-1 h-auto hover:bg-white/50"
            >
              {isCollapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
            </Button>
          )}
          
          <div className="flex items-center gap-2">
            <Hash className={`w-4 h-4 ${block.isTitle ? 'text-amber-600' : 'text-blue-600'}`} />
            <span className={`font-medium ${
              block.isTitle ? 'text-amber-800' : 'text-blue-800'
            }`}>
              {block.isTitle ? `Title ${block.titleNumber}` : `Paragraph ${block.number}`}
            </span>
          </div>
        </div>

        <Button
          variant="ghost"
          size="sm"
          onClick={() => onDelete(block.id)}
          className="text-red-600 hover:text-red-700 hover:bg-red-50 p-1 h-auto"
        >
          <Trash2 className="w-4 h-4" />
        </Button>
      </div>

      {/* Content */}
      <div className="p-4">
        <Textarea
          ref={textareaRef}
          value={localText}
          onChange={handleTextChange}
          placeholder={block.isTitle ? "Enter title text..." : "Enter paragraph text..."}
          className={`min-h-[60px] resize-none border-gray-200 focus:border-blue-400 focus:ring-2 focus:ring-blue-100 ${
            block.isTitle ? 'font-semibold text-lg bg-amber-50' : 'bg-blue-50'
          }`}
          style={{ height: 'auto' }}
        />

        {/* Statistics */}
        <div className={`mt-3 text-sm ${block.isTitle ? 'text-amber-700' : 'text-blue-700'}`}>
          <span>Words: {getWordCount()} | Characters: {getCharCount()}</span>
          {associatedStats && (
            <span className="ml-4">
              | Paragraphs: {associatedStats.count} 
              (Words: {associatedStats.words}, Characters: {associatedStats.chars})
            </span>
          )}
        </div>
      </div>
    </Card>
  );
};

export default TextBlock;
