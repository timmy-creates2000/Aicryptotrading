# Implementation Plan: Telegram Control Panel Enhancement

## Overview

This implementation plan breaks down the Telegram control panel enhancement into discrete coding tasks. The feature adds two major capabilities: (1) account balance management with Bybit API integration, and (2) strategy file upload functionality through Telegram. All tasks build incrementally, with each step validating functionality before proceeding.

## Tasks

- [ ] 1. Create balance management module with caching
  - [x] 1.1 Implement BalanceCache class with TTL support
    - Create balance_manager.py with BalanceCache class
    - Implement get(), set(), clear(), and is_fresh() methods with thread-safe locking
    - Use 30-second TTL for cache entries
    - _Requirements: 4.5, 13.1, 13.2, 13.4_
  
  - [ ]* 1.2 Write property test for cache TTL behavior
    - **Property 12: Balance Cache TTL**
    - **Validates: Requirements 4.5, 13.1, 13.2, 13.4**
  
  - [x] 1.3 Implement BalanceFetcher class for Bybit API integration
    - Create BalanceFetcher with get_balance(), get_both_balances(), and check_sufficient_balance() methods
    - Integrate with existing get_session() from trader.py
    - Use testnet=True for DEMO mode, testnet=False for REAL mode
    - Parse Bybit API response from /v5/account/wallet-balance endpoint
    - _Requirements: 1.1, 1.2, 1.5, 1.6, 1.7, 15.5_
  
  - [ ]* 1.4 Write property test for mode-based endpoint selection
    - **Property 5: Mode-Based Endpoint Selection**
    - **Validates: Requirements 1.5, 1.6, 1.7, 15.5**
  
  - [x] 1.5 Implement BalanceFormatter class for display formatting
    - Create format_display(), format_comparison(), format_currency(), and get_balance_status_emoji() methods
    - Format USDT with 2 decimal places and comma separators
    - Use emoji indicators: 🟢 > $100, 🟡 $10-$100, 🔴 < $10
    - Support HTML formatting with <b> and <code> tags
    - _Requirements: 1.3, 10.1, 10.3, 10.6_
  
  - [ ]* 1.6 Write unit tests for balance formatting
    - Test USDT formatting precision with various amounts
    - Test emoji selection for different balance thresholds
    - Test HTML tag formatting
    - _Requirements: 1.3, 10.1, 10.3, 10.6_

- [x] 2. Create strategy file upload module with validation
  - [x] 2.1 Implement FileValidator class
    - Create strategy_uploader.py with FileValidator class
    - Implement validate_file() to check extension (.txt, .md, .pdf), size (< 5MB), and content (> 50 chars)
    - Implement sanitize_filename() to remove directory traversal, convert to lowercase, replace spaces
    - Implement validate_content() for UTF-8 encoding and PDF parsing
    - _Requirements: 5.2, 5.3, 7.1, 7.2, 7.3, 7.4, 7.5, 7.7, 14.4, 14.5_
  
  - [ ]* 2.2 Write property test for file extension validation
    - **Property 15: File Extension Validation**
    - **Validates: Requirements 5.2, 7.1**
  
  - [ ]* 2.3 Write property test for filename sanitization
    - **Property 20: Filename Sanitization**
    - **Validates: Requirements 7.7, 14.4, 14.5**
  
  - [x] 2.4 Implement StrategyUploader class
    - Create StrategyUploader with download_and_save(), handle_duplicate_filename(), and reload_rag_system() methods
    - Download files from Telegram using file_id
    - Save to strategies/ folder with sanitized filenames
    - Append timestamp (_YYYYMMDD_HHMMSS) for duplicate filenames
    - Integrate with existing get_strategy_rag() for RAG reload
    - _Requirements: 5.1, 5.4, 5.6, 5.7, 14.3, 15.7_
  
  - [ ]* 2.5 Write unit tests for duplicate filename handling
    - Test timestamp appending for existing files
    - Test filename format consistency
    - _Requirements: 14.3_

- [ ] 3. Checkpoint - Ensure core modules work independently
  - Ensure all tests pass, ask the user if questions arise.

- [x] 4. Create Telegram command handlers for balance features
  - [x] 4.1 Implement KeyboardBuilder class for inline keyboards
    - Create telegram_handlers.py with KeyboardBuilder class
    - Implement build_balance_keyboard(), build_strategies_keyboard(), build_mode_switch_keyboard(), and build_strategy_preview_keyboard()
    - Organize buttons with maximum 2 per row
    - Include Back/Cancel buttons in sub-menus
    - _Requirements: 9.3, 9.5_
  
  - [x] 4.2 Implement /balance command handler
    - Create cmd_balance() function that fetches current mode balance
    - Display formatted balance with refresh button
    - Handle API errors with descriptive messages and retry button
    - _Requirements: 1.1, 1.3, 1.4, 1.8_
  
  - [ ]* 4.3 Write property test for error response structure
    - **Property 4: Error Response Structure**
    - **Validates: Requirements 1.4, 11.1, 11.2, 11.3**
  
  - [x] 4.4 Implement /accounts command handler
    - Create cmd_accounts() function that fetches both demo and real balances
    - Display side-by-side comparison with current mode indicator
    - Handle partial failures gracefully (show "unavailable" for failed balance)
    - Include mode switch buttons
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_
  
  - [x] 4.5 Implement balance refresh callback handler
    - Create handle_balance_refresh() to bypass cache and fetch fresh data
    - Update message with new balance data
    - _Requirements: 1.8, 13.3_
  
  - [x] 4.6 Implement mode switch with balance display
    - Create handle_mode_switch_with_balance() to show target mode balance before confirmation
    - Display warning if REAL mode balance < $10
    - Show both old and new mode balances
    - Include Confirm/Cancel buttons
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

- [x] 5. Create Telegram command handlers for strategy features
  - [x] 5.1 Implement /strategies command handler
    - Create cmd_strategies() function that lists all files in strategies/ folder
    - Display filename and size in KB for each file
    - Provide Preview and Delete buttons for each strategy
    - Include "Upload New Strategy" button
    - _Requirements: 6.1, 6.2, 6.3, 6.7_
  
  - [x] 5.2 Implement strategy preview callback handler
    - Create handle_strategy_preview() to display first 500 characters
    - Include "Show More" button if content > 500 characters
    - Support pagination for additional 500-character chunks
    - Use monospace formatting for content
    - _Requirements: 6.4, 12.1, 12.2, 12.3, 12.4_
  
  - [x] 5.3 Implement strategy delete callback handlers
    - Create handle_strategy_delete() to show confirmation dialog
    - Create handle_strategy_delete_confirm() to execute deletion and reload RAG
    - _Requirements: 6.5, 6.6_
  
  - [x] 5.4 Implement document upload handler
    - Create handler for Telegram document messages
    - Validate file using FileValidator
    - Download and save using StrategyUploader
    - Send confirmation with filename and size, or error message with specific reason
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7_
  
  - [ ]* 5.5 Write property test for upload success flow
    - **Property 21: Upload Success Flow**
    - **Validates: Requirements 5.4, 5.6, 5.7**
  
  - [x] 5.6 Implement /reload_strategies command handler
    - Create cmd_reload_strategies() function that triggers RAG system reload
    - Display count of loaded strategies, total character count, and timestamp
    - List any files that failed to load with error reasons
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_

- [ ] 6. Checkpoint - Ensure all command handlers work
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 7. Implement pre-trade balance validation
  - [ ] 7.1 Add balance check to trade execution flow
    - Integrate BalanceFetcher.check_sufficient_balance() into existing trade logic
    - Check that available balance >= (required_amount * 1.10)
    - Send warning message if insufficient with current balance and required amount
    - Provide buttons to reduce trade size or add funds
    - _Requirements: 4.1, 4.2, 4.3, 4.4_
  
  - [ ]* 7.2 Write property test for pre-trade balance validation
    - **Property 11: Pre-Trade Balance Validation**
    - **Validates: Requirements 4.1, 4.2, 4.3**

- [ ] 8. Implement error handling and logging
  - [ ] 8.1 Add comprehensive error handling for Bybit API errors
    - Handle error codes: 10001 (invalid key), 10003 (invalid signature), 10016 (rate limit)
    - Handle network timeouts with retry button
    - Display error code and description for unknown errors
    - Implement exponential backoff for rate limits
    - _Requirements: 11.1, 11.2, 11.3_
  
  - [ ] 8.2 Add error logging to telegram_messages.log
    - Log all API errors, validation errors, and file errors
    - Include timestamp and full context in log entries
    - _Requirements: 11.5_
  
  - [ ] 8.3 Implement graceful degradation for balance fetch failures
    - Return cached data (even if expired) when API fails
    - Display "Last known balance" with timestamp
    - Provide refresh button to retry
    - _Requirements: Error Handling section_
  
  - [ ] 8.4 Add bot_status dictionary updates
    - Update bot_status after each balance operation
    - Track operation results for monitoring
    - _Requirements: 15.6_

- [ ] 9. Integrate with existing Telegram bot infrastructure
  - [x] 9.1 Register new commands in command_callbacks dictionary
    - Add /balance, /accounts, /strategies, /reload_strategies to existing command registry
    - _Requirements: 15.3_
  
  - [x] 9.2 Register callback handlers for inline keyboard buttons
    - Add handlers for balance_refresh, mode_switch, strategy_preview, strategy_delete callbacks
    - Use existing callback routing mechanism
    - _Requirements: 15.3_
  
  - [x] 9.3 Integrate with existing send_telegram_message() and send_telegram_keyboard() functions
    - Use existing Telegram messaging functions for all responses
    - Ensure HTML parse mode is set for formatted messages
    - _Requirements: 15.4_
  
  - [x] 9.4 Add cache invalidation on mode switch
    - Clear all cached balance data when TradingConfig.set_mode() is called
    - _Requirements: 13.5_

- [x] 10. Add data models and type definitions
  - [x] 10.1 Create BalanceData dataclass
    - Define BalanceData with total_equity, available_balance, usdt_balance, coin_balances, timestamp, mode
    - Implement to_dict() and from_api_response() methods
    - _Requirements: Data Models section_
  
  - [x] 10.2 Create StrategyFileInfo dataclass
    - Define StrategyFileInfo with filename, original_filename, file_size, content_length, upload_timestamp, file_type
    - Implement to_dict() and get_display_name() methods
    - _Requirements: Data Models section_
  
  - [x] 10.3 Create ValidationResult and BalanceCheckResult dataclasses
    - Define ValidationResult with is_valid, error_message, sanitized_filename, warnings
    - Define BalanceCheckResult with is_sufficient, available_balance, required_amount, buffer_amount, warning_message
    - _Requirements: Data Models section_

- [ ] 11. Final checkpoint and integration testing
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation at key milestones
- Property tests validate universal correctness properties from the design document
- Unit tests validate specific examples and edge cases
- All code integrates with existing infrastructure (trader.py, strategy_rag.py, telegram_bot.py)
- Python is the implementation language, matching the existing codebase
