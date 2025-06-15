
import React from 'react';
import { BarChart3, FileText, Hash, Type } from 'lucide-react';
import { Card } from '@/components/ui/card';

interface TextElement {
  id: string;
  text: string;
  isTitle: boolean;
  number?: number;
  titleNumber?: number;
  visible: boolean;
}

interface StatsPanelProps {
  textBlocks: TextElement[];
}

const StatsPanel: React.FC<StatsPanelProps> = ({ textBlocks }) => {
  const totalParagraphs = textBlocks.filter(block => !block.isTitle).length;
  const totalTitles = textBlocks.filter(block => block.isTitle).length;
  
  const totalWords = textBlocks.reduce((sum, block) => {
    const words = block.text.trim() ? block.text.trim().split(/\s+/).length : 0;
    return sum + words;
  }, 0);
  
  const totalCharacters = textBlocks.reduce((sum, block) => sum + block.text.length, 0);

  const stats = [
    {
      label: 'Paragraphs',
      value: totalParagraphs,
      icon: FileText,
      color: 'text-blue-600',
      bg: 'bg-blue-100'
    },
    {
      label: 'Titles',
      value: totalTitles,
      icon: Hash,
      color: 'text-amber-600',
      bg: 'bg-amber-100'
    },
    {
      label: 'Total Words',
      value: totalWords,
      icon: Type,
      color: 'text-green-600',
      bg: 'bg-green-100'
    },
    {
      label: 'Total Characters',
      value: totalCharacters,
      icon: BarChart3,
      color: 'text-purple-600',
      bg: 'bg-purple-100'
    }
  ];

  return (
    <Card className="p-6 shadow-lg border-0 bg-white/80 backdrop-blur-sm">
      <div className="flex items-center gap-2 mb-4">
        <BarChart3 className="w-5 h-5 text-gray-700" />
        <h2 className="text-xl font-semibold text-gray-800">Statistics</h2>
      </div>
      
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {stats.map((stat) => {
          const IconComponent = stat.icon;
          return (
            <div
              key={stat.label}
              className="flex items-center gap-3 p-3 rounded-lg bg-gradient-to-r from-gray-50 to-gray-100 hover:shadow-md transition-shadow"
            >
              <div className={`p-2 rounded-full ${stat.bg}`}>
                <IconComponent className={`w-5 h-5 ${stat.color}`} />
              </div>
              <div>
                <div className="text-2xl font-bold text-gray-800">{stat.value}</div>
                <div className="text-sm text-gray-600">{stat.label}</div>
              </div>
            </div>
          );
        })}
      </div>
    </Card>
  );
};

export default StatsPanel;
