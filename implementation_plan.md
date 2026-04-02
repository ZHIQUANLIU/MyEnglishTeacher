# Implementation Plan - Optimize Word Deduplication

The user is experiencing high repetition in the English words provided by the application. This plan aims to improve the variety and uniqueness of the words by enhancing the history tracking and AI prompting logic.

## User Review Required

> [!IMPORTANT]
> The application currently only sends the last 50 seen words to the AI. I propose increasing this to 200 to give the AI more context on what to avoid. This may slightly increase API token usage but will significantly improve variety.

## Proposed Changes

### [Core Logic]

#### [MODIFY] [english_word_reminder.py](file:///c:/OpenCode/MyEnglishTeacher/english_word_reminder.py)

1.  **Increase History Buffers**:
    *   Update `MAX_USED_WORDS` from 500 to 1000 to keep a longer history of seen words.
    *   In `build_prompt`, increase the number of "already used" words sent to the AI from 50 to 200.

2.  **Client-Side Deduplication**:
    *   Modify `fetch_and_display_words` to check the words returned by the AI against the full `used_words` history.
    *   If any returned words are already in the history, they will be discarded.
    *   Implement a retry mechanism or a "fetch extra" strategy to ensure the user still gets 10 unique words if some are filtered out.

3.  **Prompt Engineering**:
    *   Refine the AI prompt to emphasize that the words must be "rare," "unique," or "different from common vocabulary" within the specified difficulty level.
    *   Add a instruction to avoid extremely common words like "the", "and", "is" (though the AI usually knows this, being explicit helps).

4.  **Randomization Improvements**:
    *   Add more variety to the `topics` and `word_types` lists to cover a broader range of vocabulary.

## Open Questions

- Should we keep a "blacklist" of words the user never wants to see again? (e.g., words they already know perfectly). For now, I'll stick to the "already seen" history.

## Verification Plan

### Automated Tests
- I will mock the API response to return a mix of "used" and "new" words and verify that the filtering logic correctly identifies and handles the duplicates.

### Manual Verification
- Run the app and trigger multiple refreshes to observe if the words remain unique.
- Check `used_words.json` to ensure the history is growing correctly.
