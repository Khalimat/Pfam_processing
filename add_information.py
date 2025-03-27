def edit_desc_file(lines, field=None, new_value=None, overwrite=False):
    """
    Edit or add a single field in DESC file content.
    
    Args:
        lines: List of strings representing the DESC file content
        field: Field to edit/add ('ID', 'DE', or 'CC')
        new_value: New text for the field
        overwrite: If True, allows overwriting even if unexpected content exists
        
    Returns:
        Modified list of strings
        
    Raises:
        ValueError: If unexpected content found and overwrite is False or invalid input
    """
    if field not in ('ID', 'DE', 'CC'):
        raise ValueError("Field must be 'ID', 'DE', or 'CC'")
    if not new_value:
        raise ValueError("New value must be provided")
    
    modified_lines = lines.copy()
    prefix = f"{field}   "
    
    # Handle ID/DE fields (strict 75-char limit)
    if field in ('ID', 'DE'):
        max_length = 75 - len(prefix)
        if len(new_value) > max_length:
            raise ValueError(f"{field} text exceeds {max_length} character limit")
        
        expected_content = "ShortName" if field == 'ID' else "Family description"
        
        for i, line in enumerate(modified_lines):
            if line.startswith(prefix):
                current_content = line[len(prefix):].strip()
                if current_content != expected_content and not overwrite:
                    raise ValueError(
                        f"Unexpected {field} content: {current_content}. "
                        f"Expected: {expected_content}"
                    )
                modified_lines[i] = f"{prefix}{new_value}\n"
                return modified_lines
        
        raise ValueError(f"{field} line not found in file")
    
    # Handle CC field (with wrapping)
    elif field == 'CC':
        # Split long CC into multiple lines
        cc_lines = []
        remaining_text = new_value
        line_prefix = "CC   "
        wrap_prefix = "CC   "
        
        while remaining_text:
            # First line uses full prefix, subsequent lines use wrap prefix
            current_prefix = line_prefix if not cc_lines else wrap_prefix
            max_chars = 75 - len(current_prefix)
            
            if len(remaining_text) <= max_chars:
                cc_lines.append(f"{current_prefix}{remaining_text}\n")
                break
            
            # Find last space before max_chars
            split_pos = remaining_text.rfind(' ', 0, max_chars)
            if split_pos == -1:  # No spaces found, force split
                split_pos = max_chars
            
            cc_lines.append(f"{current_prefix}{remaining_text[:split_pos]}\n")
            remaining_text = remaining_text[split_pos+1:]  # +1 to skip the space
        
        # Find insertion point (before first non-header line)
        insert_pos = len(modified_lines)
        header_fields = ('ID', 'DE', 'AU', 'SE', 'GA', 'TC', 'NC', 'BM', 'SM', 'TP', 'CC')
        
        for i, line in enumerate(modified_lines):
            if not any(line.startswith(f"{f}   ") for f in header_fields):
                insert_pos = i
                break
        
        # Remove existing CC if overwrite is True
        if overwrite:
            modified_lines = [line for line in modified_lines if not line.startswith("CC   ")]
            # Recalculate insert_pos after potential removal
            insert_pos = len(modified_lines)
            for i, line in enumerate(modified_lines):
                if not any(line.startswith(f"{f}   ") for f in header_fields):
                    insert_pos = i
                    break
        
        # Insert new CC lines
        for cc_line in reversed(cc_lines):
            modified_lines.insert(insert_pos, cc_line)
        
        return modified_lines


# Example usage:
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) not in (3, 4):
        print("Usage: python edit_desc.py <field> <new_value> [overwrite]")
        print("Example: python edit_desc.py DE 'New description'")
        print("Example: python edit_desc.py CC 'Long comment...' True")
        sys.exit(1)
    
    field = sys.argv[1]
    new_value = sys.argv[2]
    overwrite = len(sys.argv) > 3 and sys.argv[3].lower() == 'true'
    
    with open("DESC", "r") as f:
        lines = f.readlines()
    
    try:
        new_lines = edit_desc_file(
            lines,
            field=field,
            new_value=new_value,
            overwrite=overwrite
        )
        
        with open("DESC", "w") as f:
            f.writelines(new_lines)
        print(f"Successfully updated {field} field")
        
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
