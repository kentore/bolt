
import React, { useState, useRef, useEffect } from 'react';
import { FileText, Plus, Download, Upload, Eye, EyeOff, Trash2, Copy } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Card } from '@/components/ui/card';
import { toast } from '@/hooks/use-toast';
import TextBlock from '@/components/TextBlock';
import StatsPanel from '@/components/StatsPanel';
import OutlinePanel from '@/components/OutlinePanel';

interface TextElement {
  id: string;
  text: string;
  isTitle: boolean;
  number?: number;
  titleNumber?: number;
  visible: boolean;
}

const Index = () => {
  const [originalText, setOriginalText] = useState('');
  const [textBlocks, setTextBlocks] = useState<TextElement[]>([]);
  const [collapsedTitles, setCollapsedTitles] = useState<Set<string>>(new Set());
  const fileInputRef = useRef<HTMLInputElement>(null);
  const blockRefs = useRef<{ [key: string]: HTMLDivElement | null }>({});

  // Scroll to specific block
  const scrollToBlock = (blockId: string) => {
    const blockElement = blockRefs.current[blockId];
    if (blockElement) {
      blockElement.scrollIntoView({ 
        behavior: 'smooth', 
        block: 'center' 
      });
      // Add a brief highlight effect
      blockElement.style.boxShadow = '0 0 20px rgba(59, 130, 246, 0.5)';
      setTimeout(() => {
        blockElement.style.boxShadow = '';
      }, 1500);
    }
  };

  // Set block ref
  const setBlockRef = (blockId: string, element: HTMLDivElement | null) => {
    blockRefs.current[blockId] = element;
  };

  // Analyze text to identify titles and paragraphs with improved logic
  const analyzeTextWithTitles = (text: string): TextElement[] => {
    const lines = text.split('\n');
    const elements: Omit<TextElement, 'id' | 'visible'>[] = [];
    let i = 0;

    while (i < lines.length) {
      const currentLine = lines[i].trim();
      
      if (!currentLine) {
        i++;
        continue;
      }

      if (isTitle(currentLine, i, lines)) {
        elements.push({
          text: currentLine,
          isTitle: true
        });
      } else {
        elements.push({
          text: currentLine,
          isTitle: false
        });
      }
      
      i++;
    }

    return elements.map((el, index) => ({
      ...el,
      id: `block-${Date.now()}-${index}`,
      visible: true
    }));
  };

  // Enhanced title detection logic
  const isTitle = (line: string, index: number, allLines: string[]): boolean => {
    // 1. Must start with a number
    if (!line.match(/^\d+/)) return false;

    // 2. Check empty lines before
    let emptyLinesBefore = 0;
    for (let j = index - 1; j >= 0; j--) {
      if (allLines[j].trim() === "") {
        emptyLinesBefore++;
      } else {
        break;
      }
    }

    // 3. Check empty lines after
    let emptyLinesAfter = 0;
    for (let j = index + 1; j < allLines.length; j++) {
      if (allLines[j].trim() === "") {
        emptyLinesAfter++;
      } else {
        break;
      }
    }

    // Enhanced conditions for title detection
    const isStart = index === 0;
    const isEnd = index === allLines.length - 1;
    
    // Title if it's well separated (at least 1 empty line before AND after)
    if (emptyLinesBefore >= 1 && emptyLinesAfter >= 1) {
      return true;
    }
    
    // Title if it's at the beginning with empty lines after
    if (isStart && emptyLinesAfter >= 1) {
      return true;
    }
    
    // Title if it's at the end with empty lines before
    if (isEnd && emptyLinesBefore >= 1) {
      return true;
    }
    
    return false;
  };

  // Update numbering for all blocks
  const updateNumbering = (blocks: TextElement[]) => {
    let paragraphNumber = 1;
    let titleNumber = 1;
    
    return blocks.map(block => ({
      ...block,
      number: block.isTitle ? undefined : paragraphNumber++,
      titleNumber: block.isTitle ? titleNumber++ : undefined
    }));
  };

  // Create paragraphs from original text
  const createParagraphs = () => {
    if (!originalText.trim()) {
      toast({
        title: "Warning",
        description: "No text to convert into paragraphs",
        variant: "destructive"
      });
      return;
    }

    const elements = analyzeTextWithTitles(originalText);
    const numberedElements = updateNumbering(elements);
    setTextBlocks(numberedElements);
    setCollapsedTitles(new Set()); // Reset collapsed state
    
    const titles = numberedElements.filter(el => el.isTitle).length;
    const paragraphs = numberedElements.length - titles;
    
    toast({
      title: "Success",
      description: `Created ${titles} titles and ${paragraphs} paragraphs.`
    });
  };

  // Add empty paragraph
  const addEmptyParagraph = () => {
    const newBlock: TextElement = {
      id: `block-${Date.now()}`,
      text: '',
      isTitle: false,
      visible: true
    };
    
    const updatedBlocks = updateNumbering([...textBlocks, newBlock]);
    setTextBlocks(updatedBlocks);
  };

  // Update block text
  const updateBlockText = (id: string, newText: string) => {
    setTextBlocks(blocks => blocks.map(block => 
      block.id === id ? { ...block, text: newText } : block
    ));
  };

  // Delete block
  const deleteBlock = (id: string) => {
    const updatedBlocks = textBlocks.filter(block => block.id !== id);
    setTextBlocks(updateNumbering(updatedBlocks));
    
    // Remove from collapsed titles if it was a title
    if (collapsedTitles.has(id)) {
      const newCollapsed = new Set(collapsedTitles);
      newCollapsed.delete(id);
      setCollapsedTitles(newCollapsed);
    }
    
    toast({
      title: "Deleted",
      description: "Block deleted successfully"
    });
  };

  // Toggle title collapse
  const toggleTitleCollapse = (titleId: string, collapsed: boolean) => {
    const newCollapsed = new Set(collapsedTitles);
    if (collapsed) {
      newCollapsed.add(titleId);
    } else {
      newCollapsed.delete(titleId);
    }
    setCollapsedTitles(newCollapsed);

    const titleIndex = textBlocks.findIndex(block => block.id === titleId);
    if (titleIndex === -1) return;

    const updatedBlocks = [...textBlocks];
    
    // Find associated paragraphs (those that come after this title until next title)
    for (let i = titleIndex + 1; i < updatedBlocks.length; i++) {
      if (updatedBlocks[i].isTitle) break;
      updatedBlocks[i].visible = !collapsed;
    }
    
    setTextBlocks(updatedBlocks);
  };

  // Expand all titles
  const expandAll = () => {
    setCollapsedTitles(new Set());
    setTextBlocks(blocks => blocks.map(block => ({ ...block, visible: true })));
    toast({ title: "Expanded", description: "All sections expanded" });
  };

  // Collapse all titles
  const collapseAll = () => {
    const titleIds = textBlocks.filter(block => block.isTitle).map(block => block.id);
    setCollapsedTitles(new Set(titleIds));
    setTextBlocks(blocks => blocks.map(block => ({
      ...block,
      visible: block.isTitle ? true : false
    })));
    toast({ title: "Collapsed", description: "All sections collapsed" });
  };

  // Paste from clipboard
  const pasteText = async () => {
    try {
      const text = await navigator.clipboard.readText();
      setOriginalText(text);
      toast({ title: "Pasted", description: "Text pasted from clipboard" });
    } catch (err) {
      toast({
        title: "Error",
        description: "Could not paste from clipboard",
        variant: "destructive"
      });
    }
  };

  // Clear original text
  const clearOriginalText = () => {
    setOriginalText('');
  };

  // Clear everything
  const clearAll = () => {
    setOriginalText('');
    setTextBlocks([]);
    setCollapsedTitles(new Set());
    toast({ title: "Cleared", description: "All content cleared" });
  };

  // Save file
  const saveFile = () => {
    if (textBlocks.length === 0) {
      toast({
        title: "Warning",
        description: "No paragraphs to save",
        variant: "destructive"
      });
      return;
    }

    const content = textBlocks
      .filter(block => block.text.trim())
      .map(block => block.text)
      .join('\n\n');

    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'text-blocks.txt';
    a.click();
    URL.revokeObjectURL(url);
    
    toast({ title: "Saved", description: "File saved successfully" });
  };

  // Open file
  const openFile = () => {
    fileInputRef.current?.click();
  };

  const handleFileOpen = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
      const content = e.target?.result as string;
      setOriginalText(content);
      
      // Auto-create paragraphs
      const elements = analyzeTextWithTitles(content);
      const numberedElements = updateNumbering(elements);
      setTextBlocks(numberedElements);
      setCollapsedTitles(new Set());
      
      toast({ title: "Opened", description: "File opened and parsed successfully" });
    };
    reader.readAsText(file);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
      {/* Main container with two-panel layout */}
      <div className="container mx-auto p-6 h-screen flex flex-col">
        {/* Header */}
        <div className="text-center space-y-2 mb-6">
          <h1 className="text-4xl font-bold text-gray-800 flex items-center justify-center gap-3">
            <FileText className="text-blue-600" />
            Text Block Editor
          </h1>
          <p className="text-gray-600">Advanced paragraph and title management system</p>
        </div>

        {/* File Operations */}
        <div className="flex flex-wrap gap-3 justify-center mb-6">
          <Button onClick={openFile} variant="outline" className="gap-2">
            <Upload className="w-4 h-4" />
            Open File
          </Button>
          <Button onClick={saveFile} variant="outline" className="gap-2">
            <Download className="w-4 h-4" />
            Save File
          </Button>
          <Button onClick={expandAll} variant="outline" className="gap-2">
            <Eye className="w-4 h-4" />
            Expand All
          </Button>
          <Button onClick={collapseAll} variant="outline" className="gap-2">
            <EyeOff className="w-4 h-4" />
            Collapse All
          </Button>
          <Button onClick={clearAll} variant="destructive" className="gap-2">
            <Trash2 className="w-4 h-4" />
            Clear All
          </Button>
        </div>

        <input
          ref={fileInputRef}
          type="file"
          accept=".txt"
          onChange={handleFileOpen}
          className="hidden"
        />

        {/* Two-panel layout */}
        <div className="flex gap-6 flex-1 min-h-0">
          {/* Left Panel - Main Content */}
          <div className="flex-1 flex flex-col space-y-6 min-w-0">
            {/* Original Text Section */}
            <Card className="p-6 shadow-lg border-0 bg-white/80 backdrop-blur-sm">
              <h2 className="text-xl font-semibold mb-4 text-gray-800">Original Text</h2>
              <Textarea
                value={originalText}
                onChange={(e) => setOriginalText(e.target.value)}
                placeholder="Paste or type your text here..."
                className="min-h-[150px] text-base resize-none border-gray-200 focus:border-blue-400 focus:ring-2 focus:ring-blue-100"
              />
              <div className="flex gap-3 mt-4">
                <Button onClick={createParagraphs} className="bg-green-600 hover:bg-green-700 gap-2">
                  <FileText className="w-4 h-4" />
                  Create Paragraphs
                </Button>
                <Button onClick={pasteText} variant="outline" className="gap-2">
                  <Copy className="w-4 h-4" />
                  Paste
                </Button>
                <Button onClick={clearOriginalText} variant="outline">
                  Clear
                </Button>
                <Button onClick={addEmptyParagraph} variant="outline" className="gap-2">
                  <Plus className="w-4 h-4" />
                  Add Empty Paragraph
                </Button>
              </div>
            </Card>

            {/* Text Blocks Section */}
            <Card className="flex-1 p-6 shadow-lg border-0 bg-white/80 backdrop-blur-sm min-h-0">
              <h2 className="text-xl font-semibold mb-4 text-gray-800">Editable Blocks</h2>
              <div className="space-y-4 h-full overflow-y-auto pr-2">
                {textBlocks.length === 0 ? (
                  <div className="text-center py-12 text-gray-500">
                    <FileText className="w-12 h-12 mx-auto mb-3 opacity-50" />
                    <p>No text blocks yet. Create paragraphs from the text above.</p>
                  </div>
                ) : (
                  textBlocks
                    .filter(block => block.visible)
                    .map((block) => (
                      <div
                        key={block.id}
                        ref={(el) => setBlockRef(block.id, el)}
                      >
                        <TextBlock
                          block={block}
                          onUpdateText={updateBlockText}
                          onDelete={deleteBlock}
                          onToggleCollapse={toggleTitleCollapse}
                          textBlocks={textBlocks}
                        />
                      </div>
                    ))
                )}
              </div>
            </Card>

            {/* Statistics Panel */}
            <StatsPanel textBlocks={textBlocks} />
          </div>

          {/* Right Panel - Outline */}
          <div className="w-80 flex-shrink-0">
            <OutlinePanel 
              textBlocks={textBlocks}
              onScrollToBlock={scrollToBlock}
              collapsedTitles={collapsedTitles}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default Index;
