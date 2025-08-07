import spacy

def process_chapter_for_characters_first_occurrence():

    with open("text.txt" , "r", encoding="utf-8") as f:
        chapter_text = f.read()

    nlp = spacy.load("en_core_web_trf")

    doc = nlp(chapter_text)

    all_potential_characters = []
    replacements_to_apply = []
    
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            extended_ent_text = ent.text
            extended_start_char = ent.start_char
            extended_end_char = ent.end_char

            # check for preceding common titles(temporary fix, will have to change later)
            if ent.start > 0:
                prev_token = doc[ent.start - 1]
                if prev_token.text.lower() in ["mr.", "mrs.", "dr.", "prof.", "ms."] and \
                   (prev_token.idx + len(prev_token.text) == ent.start_char or \
                    prev_token.idx + len(prev_token.text) + 1 == ent.start_char):
                    
                    potential_full_name = chapter_text[prev_token.idx : ent.end_char]
                    if potential_full_name.startswith(prev_token.text + " " + ent.text) or \
                       potential_full_name.startswith(prev_token.text + ent.text):
                        extended_ent_text = potential_full_name
                        extended_start_char = prev_token.idx
                        extended_end_char = ent.end_char
            
            # store the extended character name and its span
            all_potential_characters.append({
                'name': extended_ent_text, 
                'start': extended_start_char, 
                'end': extended_end_char
            })

    unique_names = list(set([char['name'] for char in all_potential_characters]))
    # filter out names that are substrings of other names. TODO: does not work as expected
    filtered_proper_nouns = []
    for noun in unique_names:
        if not any(noun != other and noun in other for other in unique_names):
            filtered_proper_nouns.append(noun)
            
    all_unique_characters_found = set(filtered_proper_nouns)
    characters_wrapped_once = set()

    # iterate through the original list of potential characters to find the first occurrence
    for char_info in all_potential_characters:
        name_to_check = char_info['name']
        start_char = char_info['start']
        end_char = char_info['end']
        
        # check if this name is in our filtered list of unique characters, if it is and we haven't wrapped it yet, wrap it and add to replacements
        if name_to_check in all_unique_characters_found:
            if name_to_check not in characters_wrapped_once:
                wrapped_text = f"{{{{{name_to_check}}}}}"
                replacements_to_apply.append((start_char, end_char, wrapped_text))
                characters_wrapped_once.add(name_to_check)

    replacements_to_apply.sort(key=lambda x: x[0], reverse=True)
    text_list = list(chapter_text)

    for start_char, end_char, wrapped_text in replacements_to_apply:
        text_list[start_char:end_char] = list(wrapped_text)

    final_text = "".join(text_list)

    with open("text.txt", "w", encoding="utf-8") as f:
        f.write(final_text)

    
    return final_text, all_unique_characters_found

processed_text, unique_chars = process_chapter_for_characters_first_occurrence()
print(processed_text)
print(unique_chars)