# Requirements Document

## Introduction

This feature enhances the existing Telegram bot interface for a crypto trading bot by adding two major capabilities: (1) account balance management with real-time Bybit API integration, and (2) RAG strategy file upload functionality directly through Telegram. The goal is to create a professional, button-based control panel that minimizes typing and maximizes user experience through inline keyboards, making the bot feel like a polished trading dashboard.

## Glossary

- **Telegram_Bot**: The Python-based Telegram bot interface that receives commands and sends responses
- **Bybit_API**: The Bybit Unified Trading API used for fetching account balances and trading
- **Balance_Fetcher**: Component that retrieves account balance from Bybit API
- **Strategy_Uploader**: Component that handles file uploads from Telegram and saves to strategies/ folder
- **Inline_Keyboard**: Telegram's button-based UI that allows users to interact without typing
- **RAG_System**: Retrieval-Augmented Generation system that loads strategy documents from strategies/ folder
- **Demo_Mode**: Trading mode using Bybit testnet API with demo funds
- **Real_Mode**: Trading mode using Bybit live API with real funds
- **Control_Panel**: The button-based Telegram interface for managing the bot
- **Strategy_Document**: Text, markdown, or PDF files containing trading rules and strategies
- **File_Validator**: Component that validates uploaded files before saving

## Requirements

### Requirement 1: Account Balance Display

**User Story:** As a trader, I want to view my account balance from Bybit, so that I can monitor my available funds before placing trades.

#### Acceptance Criteria

1. WHEN a user sends /balance command, THE Telegram_Bot SHALL fetch the current balance from Bybit_API
2. THE Balance_Fetcher SHALL retrieve balance for both USDT and coin assets from the Bybit Unified Trading API
3. THE Telegram_Bot SHALL display balance with formatted currency (2 decimal places for USDT)
4. WHEN balance fetch fails, THE Telegram_Bot SHALL return a descriptive error message with retry button
5. THE Telegram_Bot SHALL show separate balances for Demo_Mode and Real_Mode based on current mode
6. THE Balance_Fetcher SHALL use testnet endpoint when Demo_Mode is active
7. THE Balance_Fetcher SHALL use live endpoint when Real_Mode is active
8. THE Telegram_Bot SHALL include refresh button in balance display for quick updates

### Requirement 2: Mode Switching with Balance Display

**User Story:** As a trader, I want to see my balance when switching between demo and real modes, so that I can verify I have sufficient funds.

#### Acceptance Criteria

1. WHEN a user switches from Demo_Mode to Real_Mode, THE Telegram_Bot SHALL display the Real_Mode balance before confirming the switch
2. WHEN a user switches from Real_Mode to Demo_Mode, THE Telegram_Bot SHALL display the Demo_Mode balance before confirming the switch
3. IF Real_Mode balance is below $10 USDT, THEN THE Telegram_Bot SHALL display a warning message
4. THE Telegram_Bot SHALL show both old and new mode balances in the confirmation message
5. THE Telegram_Bot SHALL include a cancel button in the mode switch confirmation

### Requirement 3: Account Comparison Command

**User Story:** As a trader, I want to compare my demo and real account balances side-by-side, so that I can decide which mode to use.

#### Acceptance Criteria

1. WHEN a user sends /accounts command, THE Telegram_Bot SHALL fetch balances from both Demo_Mode and Real_Mode APIs
2. THE Telegram_Bot SHALL display both balances in a formatted comparison table
3. THE Telegram_Bot SHALL indicate which mode is currently active with an emoji marker
4. THE Telegram_Bot SHALL include inline keyboard buttons to switch to either mode
5. WHEN either API call fails, THE Telegram_Bot SHALL show "unavailable" for that balance and continue displaying the other

### Requirement 4: Pre-Trade Balance Validation

**User Story:** As a trader, I want to be warned if my balance is insufficient before placing a trade, so that I can avoid failed orders.

#### Acceptance Criteria

1. WHEN the bot attempts to place a trade, THE Balance_Fetcher SHALL check current available balance
2. IF available balance is less than required trade amount plus 10% buffer, THEN THE Telegram_Bot SHALL send a warning message
3. THE Telegram_Bot SHALL include current balance and required amount in the warning message
4. THE Telegram_Bot SHALL provide buttons to either reduce trade size or add funds
5. THE Balance_Fetcher SHALL cache balance for 30 seconds to avoid excessive API calls

### Requirement 5: Strategy File Upload via Telegram

**User Story:** As a trader, I want to upload strategy documents directly through Telegram, so that I can update my trading rules without accessing the server.

#### Acceptance Criteria

1. WHEN a user sends a document file to Telegram_Bot, THE Strategy_Uploader SHALL download the file
2. THE File_Validator SHALL verify the file extension is .txt, .md, or .pdf
3. THE File_Validator SHALL verify the file size is less than 5MB
4. IF file validation passes, THEN THE Strategy_Uploader SHALL save the file to strategies/ folder
5. IF file validation fails, THEN THE Telegram_Bot SHALL return an error message explaining the validation failure
6. WHEN file upload succeeds, THE Telegram_Bot SHALL confirm with file name and size
7. THE Strategy_Uploader SHALL reload the RAG_System after successful upload
8. THE Telegram_Bot SHALL provide an inline keyboard button to preview the uploaded strategy

### Requirement 6: Strategy Management Interface

**User Story:** As a trader, I want to manage my strategy documents through buttons, so that I can organize my trading rules professionally.

#### Acceptance Criteria

1. WHEN a user sends /strategies command, THE Telegram_Bot SHALL list all files in strategies/ folder
2. THE Telegram_Bot SHALL display file name and size in KB for each strategy document
3. THE Telegram_Bot SHALL provide inline keyboard buttons for each strategy: Preview, Delete, Rename
4. WHEN a user clicks Preview button, THE Telegram_Bot SHALL display the first 500 characters of the strategy
5. WHEN a user clicks Delete button, THE Telegram_Bot SHALL show a confirmation dialog with Yes/No buttons
6. WHEN delete is confirmed, THE Strategy_Uploader SHALL remove the file and reload RAG_System
7. THE Telegram_Bot SHALL include a "Upload New Strategy" button in the strategies list

### Requirement 7: Strategy File Validation

**User Story:** As a developer, I want uploaded files to be validated, so that invalid files don't break the RAG system.

#### Acceptance Criteria

1. THE File_Validator SHALL reject files with extensions other than .txt, .md, or .pdf
2. THE File_Validator SHALL reject files larger than 5MB
3. THE File_Validator SHALL reject files with less than 50 characters of content
4. THE File_Validator SHALL check for valid UTF-8 encoding in text files
5. WHEN a PDF file is uploaded, THE File_Validator SHALL verify it can be parsed by PyPDF2
6. IF PyPDF2 is not installed, THEN THE Telegram_Bot SHALL reject PDF uploads with installation instructions
7. THE File_Validator SHALL sanitize file names to prevent directory traversal attacks

### Requirement 8: Strategy Reload Command

**User Story:** As a trader, I want to reload strategies without restarting the bot, so that I can apply new rules immediately.

#### Acceptance Criteria

1. WHEN a user sends /reload_strategies command, THE RAG_System SHALL re-scan the strategies/ folder
2. THE RAG_System SHALL reload all valid strategy documents
3. THE Telegram_Bot SHALL display count of loaded strategies and total character count
4. THE Telegram_Bot SHALL list any files that failed to load with error reasons
5. THE Telegram_Bot SHALL confirm successful reload with timestamp

### Requirement 9: Professional Button-Based Interface

**User Story:** As a trader, I want all features accessible through buttons, so that I can control the bot without typing commands.

#### Acceptance Criteria

1. THE Telegram_Bot SHALL use inline keyboards for all interactive features
2. THE Telegram_Bot SHALL include emoji icons in all button labels for visual clarity
3. THE Telegram_Bot SHALL organize buttons in logical rows with maximum 2 buttons per row
4. WHEN a button action completes, THE Telegram_Bot SHALL update the message with results
5. THE Telegram_Bot SHALL include a "Back" or "Cancel" button in all sub-menus
6. THE Telegram_Bot SHALL use callback queries for all button interactions
7. THE Telegram_Bot SHALL provide visual feedback (loading message) for operations taking more than 2 seconds

### Requirement 10: Balance Display Formatting

**User Story:** As a trader, I want balance information displayed clearly, so that I can quickly understand my account status.

#### Acceptance Criteria

1. THE Telegram_Bot SHALL format USDT amounts with 2 decimal places and comma separators
2. THE Telegram_Bot SHALL format coin amounts with appropriate decimal places based on coin value
3. THE Telegram_Bot SHALL use emoji indicators for balance status (🟢 for sufficient, 🟡 for low, 🔴 for critical)
4. THE Telegram_Bot SHALL display balance change percentage if previous balance is cached
5. THE Telegram_Bot SHALL show last update timestamp in HH:MM:SS format
6. THE Telegram_Bot SHALL use HTML formatting for bold labels and monospace for numbers

### Requirement 11: Error Handling and User Feedback

**User Story:** As a trader, I want clear error messages when operations fail, so that I can understand what went wrong and how to fix it.

#### Acceptance Criteria

1. WHEN Bybit_API returns an error, THE Telegram_Bot SHALL display the error code and description
2. WHEN network timeout occurs, THE Telegram_Bot SHALL display "Connection timeout" with retry button
3. WHEN API credentials are invalid, THE Telegram_Bot SHALL display "Invalid API keys" with setup instructions
4. WHEN file upload fails, THE Telegram_Bot SHALL display specific reason (size, format, encoding)
5. THE Telegram_Bot SHALL log all errors to telegram_messages.log with timestamp and context
6. THE Telegram_Bot SHALL provide actionable next steps in all error messages

### Requirement 12: Strategy Preview and Content Display

**User Story:** As a trader, I want to preview strategy content before applying it, so that I can verify the rules are correct.

#### Acceptance Criteria

1. WHEN a user clicks Preview button for a strategy, THE Telegram_Bot SHALL display the first 500 characters
2. THE Telegram_Bot SHALL include "Show More" button if content exceeds 500 characters
3. WHEN "Show More" is clicked, THE Telegram_Bot SHALL display next 500 characters
4. THE Telegram_Bot SHALL use monospace formatting for strategy content display
5. THE Telegram_Bot SHALL include "Apply" and "Cancel" buttons after preview
6. WHEN "Apply" is clicked, THE RAG_System SHALL mark that strategy as active for next trade analysis

### Requirement 13: Balance Caching and Performance

**User Story:** As a developer, I want balance requests to be cached, so that we don't exceed Bybit API rate limits.

#### Acceptance Criteria

1. THE Balance_Fetcher SHALL cache balance data for 30 seconds
2. WHEN cached data exists and is less than 30 seconds old, THE Balance_Fetcher SHALL return cached data
3. WHEN user clicks refresh button, THE Balance_Fetcher SHALL bypass cache and fetch fresh data
4. THE Balance_Fetcher SHALL store cache in memory with timestamp
5. THE Balance_Fetcher SHALL clear cache when mode is switched

### Requirement 14: Strategy File Naming and Organization

**User Story:** As a trader, I want uploaded files to have clear names, so that I can identify strategies easily.

#### Acceptance Criteria

1. WHEN a file is uploaded without a custom name, THE Strategy_Uploader SHALL use the original filename
2. THE Telegram_Bot SHALL provide option to rename file during upload via inline keyboard
3. THE Strategy_Uploader SHALL append timestamp to duplicate filenames to prevent overwrites
4. THE Strategy_Uploader SHALL convert spaces to underscores in filenames
5. THE Strategy_Uploader SHALL convert filenames to lowercase for consistency
6. THE Telegram_Bot SHALL display both original and saved filename in confirmation message

### Requirement 15: Integration with Existing Trading Flow

**User Story:** As a developer, I want the new features to integrate seamlessly with existing code, so that current functionality is not disrupted.

#### Acceptance Criteria

1. THE Balance_Fetcher SHALL use the existing get_session() function from trader.py
2. THE Strategy_Uploader SHALL use the existing StrategyRAG class from strategy_rag.py
3. THE Telegram_Bot SHALL register new commands in the existing command_callbacks dictionary
4. THE Telegram_Bot SHALL use existing send_telegram_message() and send_telegram_keyboard() functions
5. THE Balance_Fetcher SHALL respect current Demo_Mode or Real_Mode from TradingConfig
6. THE Telegram_Bot SHALL update bot_status dictionary when balance operations complete
7. THE Strategy_Uploader SHALL trigger RAG reload using existing get_strategy_rag() function
