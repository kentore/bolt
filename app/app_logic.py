import re
from .utils import generate_unique_id

# TextBlock structure:
# {'id': str, 'text': str, 'is_title': bool, 'visible': bool, 'display_number': str}

class AppLogic:
    def __init__(self):
        self.original_text = ""
        self.text_blocks: list[dict] = []
        self.collapsed_title_ids: set[str] = set()

    def _is_title(self, line: str, index: int, all_lines: list[str]) -> bool:
        """
        Determines if a line is a title based on specific criteria.
        - Must start with one or more digits.
        - Considers empty lines before and after.
        """
        line = line.strip()
        if not line: # Should not happen if called from analyze_and_create_blocks after skipping empty lines
            return False

        if not re.match(r"^\d+", line):
            return False

        empty_lines_before = 0
        # Count empty lines before
        for i in range(index - 1, -1, -1):
            if not all_lines[i].strip():
                empty_lines_before += 1
            else:
                break

        empty_lines_after = 0
        # Count empty lines after
        for i in range(index + 1, len(all_lines)):
            if not all_lines[i].strip():
                empty_lines_after += 1
            else:
                break

        # Conditions for being a title
        if index == 0: # First line
            return empty_lines_after >= 1
        elif index == len(all_lines) - 1: # Last line
            return empty_lines_before >= 1
        else: # Lines in between
            return empty_lines_before >= 1 and empty_lines_after >= 1

        return False

    def analyze_and_create_blocks(self, full_text: str) -> list[dict]:
        """
        Analyzes the full text, splits it into lines, and creates basic text blocks.
        """
        lines = full_text.splitlines() # Use splitlines to handle different newline chars consistently
        raw_blocks = []

        stripped_lines = [line.strip() for line in lines] # Pre-strip for _is_title checks on empty lines

        for i, line_content in enumerate(lines):
            trimmed_line = line_content.strip()
            if not trimmed_line:
                continue  # Skip empty lines

            is_title_block = self._is_title(trimmed_line, i, stripped_lines) # Pass stripped_lines for context

            block = {
                'id': generate_unique_id(),
                'text': trimmed_line,
                'is_title': is_title_block,
                'visible': True, # Default visibility
                'display_number': "" # To be filled by _assign_block_numbers
            }
            raw_blocks.append(block)

        return raw_blocks

    def _assign_block_numbers(self, blocks: list[dict]) -> list[dict]:
        """
        Assigns display numbers to blocks (e.g., "Title 1", "1.", "2.").
        """
        paragraph_number = 1
        title_number = 1
        for block in blocks:
            if block['is_title']:
                block['display_number'] = f"Title {title_number}"
                title_number += 1
            else:
                block['display_number'] = f"{paragraph_number}."
                paragraph_number += 1
        return blocks

    def process_original_text(self, original_text_content: str):
        """
        Processes the original text to generate structured text blocks.
        """
        self.original_text = original_text_content
        raw_blocks = self.analyze_and_create_blocks(original_text_content)
        self.text_blocks = self._assign_block_numbers(raw_blocks)
        self.collapsed_title_ids = set()
        # print(f"Processed blocks: {self.text_blocks}") # For debugging

    def add_empty_paragraph(self, index: int = -1):
        """
        Adds a new empty paragraph block, optionally at a specific index.
        If index is -1, adds to the end.
        """
        new_block = {
            'id': generate_unique_id(),
            'text': '',
            'is_title': False,
            'visible': True,
            'display_number': '' # Will be set by _assign_block_numbers
        }
        if index == -1 or index >= len(self.text_blocks):
            self.text_blocks.append(new_block)
        else:
            self.text_blocks.insert(index, new_block)

        self.text_blocks = self._assign_block_numbers(self.text_blocks)
        return new_block['id'] # Return new block's ID

    def delete_block(self, block_id: str):
        """
        Deletes a block by its ID.
        """
        self.text_blocks = [b for b in self.text_blocks if b['id'] != block_id]
        self.text_blocks = self._assign_block_numbers(self.text_blocks) # Re-assign numbers

    def update_block_text(self, block_id: str, new_text: str):
        """
        Updates the text of a specific block.
        """
        for block in self.text_blocks:
            if block['id'] == block_id:
                block['text'] = new_text
                # No re-numbering needed for just a text update
                break

    def toggle_block_title_status(self, block_id: str, is_title: bool):
        """
        Toggles the title status of a block and re-assigns numbers.
        """
        block_found = False
        for block in self.text_blocks:
            if block['id'] == block_id:
                block['is_title'] = is_title
                block_found = True
                break
        if block_found:
            self.text_blocks = self._assign_block_numbers(self.text_blocks)

    def toggle_title_expansion(self, title_id: str):
        """
        Toggles the visibility of paragraphs under a specific title.
        """
        title_block_index = -1
        is_currently_collapsed = title_id in self.collapsed_title_ids

        for i, block in enumerate(self.text_blocks):
            if block['id'] == title_id:
                if not block['is_title']:
                    return # Not a title, do nothing
                title_block_index = i
                break

        if title_block_index == -1:
            return # Title ID not found

        if is_currently_collapsed:
            self.collapsed_title_ids.remove(title_id)
            expanded_state_for_children = True
        else:
            self.collapsed_title_ids.add(title_id)
            expanded_state_for_children = False

        # Update visibility of subsequent blocks until the next title
        for i in range(title_block_index + 1, len(self.text_blocks)):
            block = self.text_blocks[i]
            if block['is_title']:
                break # Stop at the next title
            block['visible'] = expanded_state_for_children

    def expand_all(self):
        """
        Expands all titles and makes all blocks visible.
        """
        self.collapsed_title_ids.clear()
        for block in self.text_blocks:
            block['visible'] = True

    def collapse_all(self):
        """
        Collapses all titles, hiding their paragraphs. Titles remain visible.
        """
        self.collapsed_title_ids.clear() # Start fresh
        for block in self.text_blocks:
            if block['is_title']:
                self.collapsed_title_ids.add(block['id'])
                block['visible'] = True # Titles themselves are always visible
            else:
                # Paragraphs are initially hidden; toggle_title_expansion will make them visible if their parent is expanded
                # This logic is a bit tricky: if we just set all non-titles to false, they stay false.
                # The actual visibility is determined by iterating after setting collapsed_title_ids.
                pass # Visibility will be set based on collapsed_title_ids state

        # After identifying all titles to collapse, iterate and set visibility
        currently_under_collapsed_title = False
        for block in self.text_blocks:
            if block['is_title']:
                if block['id'] in self.collapsed_title_ids:
                    currently_under_collapsed_title = True
                else: # This case should ideally not happen if we just added all to collapsed_title_ids
                    currently_under_collapsed_title = False
                block['visible'] = True # Titles are always visible
            else: # Paragraph
                if currently_under_collapsed_title:
                    block['visible'] = False
                else: # Should not happen if all titles were added to collapsed_ids
                    block['visible'] = True

    def get_text_for_saving(self) -> str:
        """
        Constructs a string for saving, including only visible, non-empty blocks,
        separated by double newlines.
        """
        lines = []
        for block in self.text_blocks:
            # Only save blocks that are currently marked as visible AND have some actual content
            if block.get('visible', True) and block.get('text', '').strip():
                lines.append(block.get('text', ''))

        # Join with double newlines, similar to the reference web app's behavior
        return "\n\n".join(lines)

    def calculate_stats(self) -> dict:
        """
        Calculates various statistics about the text blocks.
        """
        stats = {
            'titles': 0,
            'paragraphs': 0,
            'words': 0,
            'visible_blocks': 0,
            'total_blocks': len(self.text_blocks)
        }

        for block in self.text_blocks:
            if block.get('visible', True): # Consider block visible by default if key is missing
                stats['visible_blocks'] += 1
                if block.get('is_title', False):
                    stats['titles'] += 1
                else:
                    stats['paragraphs'] += 1

                # Calculate words for visible blocks based on their text content
                stats['words'] += len(block.get('text', '').split())

        return stats

    def clear_all_data(self):
        """
        Resets all application data to its initial empty state.
        """
        self.original_text = ""
        self.text_blocks = []
        self.collapsed_title_ids.clear()
