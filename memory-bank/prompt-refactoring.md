# Prompt Text Refactoring

2025-07-26 19:15:52 - Technical design for refactoring prompt texts.

## Issue Identified

The current implementation of user input prompts in `main.py` causes duplicate display of default values:

1. The prompt text includes default values in square brackets: `f"Symbole crypto [{default_symbol}]: "`
2. The Rich library's `Prompt.ask()` function automatically adds default values in parentheses

This results in redundant display like: `"Symbole crypto [BTC-USD]: (BTC-USD):"`

## Proposed Changes

### Locations to Modify

The following prompt texts need to be modified in `main.py`:

1. Line 493: `symbol = get_user_input(f"Symbole crypto [{default_symbol}]: ", str, default_symbol)`
2. Line 498: `period = get_user_input(f"Période [{PeriodTranslator.get_period_description(default_period)}]: ", str, default_period)`
3. Line 502: `short_window = get_user_input(f"SMA courte [{default_short}]: ", int, default_short)`
4. Line 506: `long_window = get_user_input(f"SMA longue [{default_long}]: ", int, default_long)`
5. Line 545: `symbol = get_user_input(f"Symbole crypto [{default_symbol}]: ", str, default_symbol)`
6. Line 550: `period = get_user_input(f"Période [{PeriodTranslator.get_period_description(default_period)}]: ", str, default_period)`

### Implementation

For each location, remove the default value from the prompt string:

```python
# Original
symbol = get_user_input(f"Symbole crypto [{default_symbol}]: ", str, default_symbol)

# Changed
symbol = get_user_input("Symbole crypto: ", str, default_symbol)
```

Similarly for the period prompts:

```python
# Original
period = get_user_input(f"Période [{PeriodTranslator.get_period_description(default_period)}]: ", str, default_period)

# Changed
period = get_user_input("Période: ", str, default_period)
```

### Benefits

1. Cleaner user interface without redundant information
2. Maintains the same functionality as default values are still passed to the Prompt.ask() function
3. Improves readability of the command line interface

## Implementation Steps

1. Switch to Code mode to implement these changes
2. Test each prompt to ensure proper functioning after changes
3. Verify the UI experience is improved with the default values displayed only once