# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based web automation project for booking tennis courts on tennis.paris.fr. The system automates the reservation process using Selenium WebDriver with Chrome browser automation.

## Development Commands

### Running the Application
```bash
python bot.py                    # Run main bot (default profile)
python bot.py training           # Run in training mode (no actual booking)
python bot2.py                   # Run bot for profile 2
python bot3.py                   # Run bot for profile 3
```

### Dependencies
Install required packages (no requirements.txt exists):
```bash
pip install selenium webdriver-manager PyYAML
```

## Code Architecture

### Main Components
- `bot.py` - Core implementation with `paris_tennis()` function
- `bot2.py`, `bot3.py` - Profile-specific variants importing from bot.py
- `bot copy.py` - Modified version with different availability logic
- `config.yaml` - User credentials and settings (git-ignored, external path)

### Key Function: `paris_tennis()`
Located in `bot.py`, this is the main automation function with parameters for:
- User profile selection (1, 2, or 3)
- Court preferences (covered/uncovered, specific court numbers)
- Time scheduling (hour to start execution)
- Training mode toggle
- Retry and timeout configurations

### Automation Flow
1. Chrome browser setup with specific window size and language settings
2. Multi-window authentication using config.yaml credentials
3. Court filtering by coverage, location, and availability
4. Continuous refresh monitoring until desired slots appear
5. Automated booking form completion

## Development Notes

### Code Style
- Mixed French/English naming (French for domain terms: `jours`, `disponibilites`)
- Extensive debug print statements for execution monitoring
- Chrome-only browser support with deprecated Selenium methods

### Configuration
- External config file: `/Users/jauffret/code/MartinJ9678/paristennis/config.yaml`
- Contains user credentials, court preferences, and personal information
- File path may need adjustment for different development environments

### Error Handling
- Built-in retry logic for `StaleElementReferenceException`
- Training mode prevents actual bookings during testing
- Time-based execution delays until specified hour

### Missing Infrastructure
- No requirements.txt (manual pip install needed)
- No test framework or lint configuration
- No formal documentation beyond code comments