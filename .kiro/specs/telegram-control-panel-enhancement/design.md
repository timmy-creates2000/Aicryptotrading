# Design Document: Telegram Control Panel Enhancement

## Overview

This design specifies the technical implementation for enhancing the Telegram bot interface with two major capabilities: (1) real-time account balance management through Bybit API integration, and (2) strategy file upload functionality via Telegram for the RAG system.

### Goals

- Enable traders to view and monitor Bybit account balances (demo and real) directly through Telegram
- Provide pre-trade balance validation to prevent failed orders due to insufficient funds
- Allow traders to upload, manage, and preview strategy documents through Telegram without server access
- Create a professional button-based interface that minimizes typing and maximizes user experience
- Integrate seamlessly with existing trading bot infrastructure without disrupting current functionality

### Non-Goals

- Full portfolio management or historical balance tracking
- Advanced file editing capabilities within Telegram
- Multi-exchange support (only Bybit)
- Real-time balance streaming or WebSocket connections

### Success Metrics

- Balance fetch operations complete within 2 seconds
- Zero failed trades due to insufficient balance (with proper validation)
- Strategy file uploads succeed with 99%+ reliability
- All interactive features accessible through inline keyboard buttons
- API rate limits respected (no 429 errors under normal usage)

## Architecture

### System Components

The enhancement adds three new modules to the existing trading bot architecture:

```
telegram_bot.py (existing)
telegram_commands.py (existing)
├── balance_manager.py (NEW)
│   ├── BalanceFetcher
│   ├── BalanceCache
│   └── BalanceFormatter
├── strategy_uploader.py (NEW)
│   ├── FileValidator
│   ├── StrategyUploader
│   └── FileManager
└── telegram_handlers.py (NEW)
    ├── BalanceHandlers
    ├── StrategyHandlers
    └── KeyboardBuilder
```

### Integration Points

1. **Bybit API Integration**
   - Uses existing `get_session()` from `trader.py`
   - Respects current mode (Demo/Real) from `TradingConfig`
   - Leverages existing API credentials from `.env`

2. **RAG System Integration**
   - Uses existing `StrategyRAG` class from `strategy_rag.py`
   - Calls `get_strategy_rag()` for reload operations
   - Saves files to existing `strategies/` folder

3. **Telegram Bot Integration**
   - Registers new commands in existing `command_callbacks` dictionary
   - Uses existing `send_telegram_message()` and `send_telegram_keyboard()` functions
   - Updates `bot_status` dictionary for state management

### Data Flow

#### Balance Fetch Flow
```
User → /balance command
  → BalanceHandlers.handle_balance()
    → BalanceFetcher.get_balance(mode)
      → Check BalanceCache (30s TTL)
        → If cached: return cached data
        → If expired: fetch from Bybit API
          → get_session() from trader.py
          → API call to /v5/account/wallet-balance
          → Parse and format response
          → Store in cache
      → BalanceFormatter.format_display()
    → send_telegram_keyboard() with refresh button
```

#### Strategy Upload Flow
```
User → Sends document file
  → telegram_webhook() receives file
    → FileValidator.validate_file()
      → Check extension (.txt, .md, .pdf)
      → Check size (< 5MB)
      → Check content (> 50 chars)
      → Sanitize filename
    → StrategyUploader.download_and_save()
      → Download from Telegram servers
      → Save to strategies/ folder
      → get_strategy_rag().load_strategies()
    → send_telegram_message() with confirmation
```

## Components and Interfaces

### 1. BalanceFetcher

**Purpose**: Fetch account balance from Bybit API with caching

**Class Definition**:
```python
class BalanceFetcher:
    def __init__(self):
        self.cache = BalanceCache()
    
    def get_balance(self, mode: str = "DEMO") -> dict:
        """
        Fetch balance for specified mode (DEMO or REAL).
        Returns cached data if available and fresh.
        
        Returns:
            {
                "total_equity": float,
                "available_balance": float,
                "usdt_balance": float,
                "coin_balances": dict,
                "timestamp": str,
                "mode": str
            }
        """
    
    def get_both_balances(self) -> dict:
        """
        Fetch both demo and real balances for comparison.
        
        Returns:
            {
                "demo": balance_dict,
                "real": balance_dict,
                "current_mode": str
            }
        """
    
    def check_sufficient_balance(self, required_amount: float, mode: str) -> tuple[bool, float]:
        """
        Check if balance is sufficient for trade with 10% buffer.
        
        Returns:
            (is_sufficient: bool, available_balance: float)
        """
```

**API Integration**:
- Endpoint: `GET /v5/account/wallet-balance`
- Parameters: `accountType=UNIFIED`, `coin=USDT`
- Authentication: Uses existing API keys from `get_session()`

### 2. BalanceCache

**Purpose**: In-memory cache for balance data to avoid rate limits

**Class Definition**:
```python
class BalanceCache:
    def __init__(self, ttl_seconds: int = 30):
        self.cache = {}  # {mode: {data: dict, timestamp: float}}
        self.ttl = ttl_seconds
        self.lock = threading.Lock()
    
    def get(self, mode: str) -> dict | None:
        """Get cached balance if not expired"""
    
    def set(self, mode: str, data: dict):
        """Store balance data with timestamp"""
    
    def clear(self, mode: str = None):
        """Clear cache for specific mode or all"""
    
    def is_fresh(self, mode: str) -> bool:
        """Check if cached data is within TTL"""
```

### 3. BalanceFormatter

**Purpose**: Format balance data for Telegram display

**Class Definition**:
```python
class BalanceFormatter:
    @staticmethod
    def format_display(balance: dict) -> str:
        """
        Format balance for single mode display.
        Includes emoji indicators and formatted numbers.
        """
    
    @staticmethod
    def format_comparison(demo_balance: dict, real_balance: dict, current_mode: str) -> str:
        """
        Format side-by-side comparison of demo and real balances.
        Marks current mode with emoji.
        """
    
    @staticmethod
    def format_currency(amount: float, decimals: int = 2) -> str:
        """Format currency with comma separators"""
    
    @staticmethod
    def get_balance_status_emoji(balance: float) -> str:
        """
        Return emoji based on balance level:
        🟢 > $100, 🟡 $10-$100, 🔴 < $10
        """
```

### 4. FileValidator

**Purpose**: Validate uploaded files before saving

**Class Definition**:
```python
class FileValidator:
    ALLOWED_EXTENSIONS = ['.txt', '.md', '.pdf']
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
    MIN_CONTENT_LENGTH = 50
    
    @staticmethod
    def validate_file(file_info: dict) -> tuple[bool, str]:
        """
        Validate file meets all requirements.
        
        Args:
            file_info: {
                "file_name": str,
                "file_size": int,
                "mime_type": str
            }
        
        Returns:
            (is_valid: bool, error_message: str)
        """
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitize filename to prevent directory traversal.
        - Convert to lowercase
        - Replace spaces with underscores
        - Remove special characters
        - Prevent path traversal (../)
        """
    
    @staticmethod
    def validate_content(content: bytes, extension: str) -> tuple[bool, str]:
        """
        Validate file content based on type.
        - Text files: check UTF-8 encoding and min length
        - PDF files: verify PyPDF2 can parse
        """
```

### 5. StrategyUploader

**Purpose**: Handle file downloads and saves to strategies folder

**Class Definition**:
```python
class StrategyUploader:
    def __init__(self, strategies_folder: str = "strategies"):
        self.folder = strategies_folder
        self.validator = FileValidator()
    
    def download_and_save(self, file_id: str, original_filename: str) -> tuple[bool, str, dict]:
        """
        Download file from Telegram and save to strategies folder.
        
        Args:
            file_id: Telegram file ID
            original_filename: Original filename from user
        
        Returns:
            (success: bool, saved_filename: str, file_info: dict)
        """
    
    def handle_duplicate_filename(self, filename: str) -> str:
        """
        Append timestamp to filename if it already exists.
        Example: strategy.txt → strategy_20240115_143022.txt
        """
    
    def reload_rag_system(self) -> tuple[bool, str]:
        """
        Reload RAG system after file upload.
        Returns success status and message.
        """
```

### 6. Telegram Command Handlers

**New Commands**:

```python
@register_command("balance")
def cmd_balance():
    """Display current account balance with refresh button"""

@register_command("accounts")
def cmd_accounts():
    """Display side-by-side comparison of demo and real balances"""

@register_command("strategies")
def cmd_strategies():
    """List all strategy documents with management buttons"""

@register_command("reload_strategies")
def cmd_reload_strategies():
    """Reload RAG system from strategies folder"""
```

**Callback Handlers**:

```python
def handle_balance_refresh(mode: str, chat_id: str):
    """Handle refresh button click - bypass cache"""

def handle_strategy_preview(filename: str, chat_id: str, offset: int = 0):
    """Show 500 chars of strategy content with pagination"""

def handle_strategy_delete(filename: str, chat_id: str):
    """Show confirmation dialog for file deletion"""

def handle_strategy_delete_confirm(filename: str, chat_id: str):
    """Execute file deletion and reload RAG"""

def handle_mode_switch_with_balance(new_mode: str, chat_id: str):
    """Show balance before confirming mode switch"""
```

### 7. KeyboardBuilder

**Purpose**: Build inline keyboard layouts for various features

**Class Definition**:
```python
class KeyboardBuilder:
    @staticmethod
    def build_balance_keyboard(mode: str) -> list:
        """
        Build keyboard for balance display.
        Buttons: [Refresh] [Switch Mode] [Compare]
        """
    
    @staticmethod
    def build_strategies_keyboard(strategies: list) -> list:
        """
        Build keyboard for strategy management.
        Each strategy gets: [Preview] [Delete]
        Plus: [Upload New] [Reload]
        """
    
    @staticmethod
    def build_mode_switch_keyboard(current_mode: str, new_balance: dict) -> list:
        """
        Build keyboard for mode switch confirmation.
        Shows balance and buttons: [Confirm] [Cancel]
        """
    
    @staticmethod
    def build_strategy_preview_keyboard(filename: str, has_more: bool) -> list:
        """
        Build keyboard for strategy preview.
        Buttons: [Show More] [Apply] [Back]
        """
```


## Data Models

### BalanceData

```python
@dataclass
class BalanceData:
    """Represents account balance information"""
    total_equity: float
    available_balance: float
    usdt_balance: float
    coin_balances: dict[str, float]  # {coin: amount}
    timestamp: datetime
    mode: str  # "DEMO" or "REAL"
    
    def to_dict(self) -> dict:
        """Convert to dictionary for caching"""
    
    @classmethod
    def from_api_response(cls, response: dict, mode: str) -> 'BalanceData':
        """Parse Bybit API response into BalanceData"""
```

### StrategyFileInfo

```python
@dataclass
class StrategyFileInfo:
    """Represents a strategy document file"""
    filename: str
    original_filename: str
    file_size: int
    content_length: int
    upload_timestamp: datetime
    file_type: str  # "txt", "md", "pdf"
    
    def to_dict(self) -> dict:
        """Convert to dictionary for display"""
    
    def get_display_name(self) -> str:
        """Get formatted name for Telegram display"""
```

### ValidationResult

```python
@dataclass
class ValidationResult:
    """Result of file validation"""
    is_valid: bool
    error_message: str
    sanitized_filename: str
    warnings: list[str]
```

### BalanceCheckResult

```python
@dataclass
class BalanceCheckResult:
    """Result of pre-trade balance check"""
    is_sufficient: bool
    available_balance: float
    required_amount: float
    buffer_amount: float
    warning_message: str
```

## Bybit API Specifications

### Wallet Balance Endpoint

**Endpoint**: `GET /v5/account/wallet-balance`

**Request Parameters**:
```python
{
    "accountType": "UNIFIED",  # Unified trading account
    "coin": "USDT"  # Optional: filter by coin
}
```

**Response Structure**:
```json
{
    "retCode": 0,
    "retMsg": "OK",
    "result": {
        "list": [
            {
                "totalEquity": "1000.50",
                "accountIMRate": "0",
                "totalMarginBalance": "1000.50",
                "totalAvailableBalance": "950.25",
                "coin": [
                    {
                        "coin": "USDT",
                        "equity": "1000.50",
                        "availableToWithdraw": "950.25",
                        "walletBalance": "1000.50"
                    }
                ]
            }
        ]
    }
}
```

**Error Handling**:
- `10001`: Invalid API key → Display setup instructions
- `10003`: Invalid signature → Display credential error
- `10016`: Rate limit exceeded → Use cached data, show retry button
- Network timeout → Display connection error with retry

### API Rate Limits

- **Wallet Balance**: 120 requests per minute
- **Strategy**: Cache for 30 seconds to stay well under limit
- **Burst Protection**: Implement exponential backoff on errors

## Telegram Bot API Specifications

### File Download Flow

1. **Get File Info**:
```python
GET https://api.telegram.org/bot{token}/getFile?file_id={file_id}

Response:
{
    "ok": true,
    "result": {
        "file_id": "...",
        "file_unique_id": "...",
        "file_size": 12345,
        "file_path": "documents/file_123.txt"
    }
}
```

2. **Download File**:
```python
GET https://api.telegram.org/file/bot{token}/{file_path}

Returns: Raw file bytes
```

### Inline Keyboard Format

```python
{
    "inline_keyboard": [
        [
            {"text": "🔄 Refresh", "callback_data": "balance_refresh_DEMO"},
            {"text": "📊 Compare", "callback_data": "balance_compare"}
        ],
        [
            {"text": "🔄 Switch to REAL", "callback_data": "mode_switch_REAL"}
        ]
    ]
}
```

### Message Formatting

- **Parse Mode**: HTML
- **Bold**: `<b>text</b>`
- **Italic**: `<i>text</i>`
- **Monospace**: `<code>text</code>`
- **Max Length**: 4096 characters per message


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property Reflection

After analyzing all acceptance criteria, I identified several areas of redundancy:

1. **Extension validation** (5.2, 7.1): Both specify the same validation rule - combined into one property
2. **Size validation** (5.3, 7.2): Duplicate specifications - combined into one property
3. **Mode-specific endpoint selection** (1.6, 1.7): Two sides of the same property - combined
4. **Mode switching with balance** (2.1, 2.2): Same behavior in both directions - combined
5. **Filename sanitization** (14.4, 14.5): Both are transformations applied together - combined
6. **Cache behavior** (13.1, 13.2): Cache TTL and cache hit are the same property - combined
7. **Error message structure** (11.1, 11.2, 11.3, 11.4): All follow same pattern - combined into error handling property
8. **Keyboard structure properties** (1.8, 2.5, 3.4, 5.8, 6.7, 9.3, 9.5): Multiple properties about button presence - consolidated

The following properties represent the unique, non-redundant validation requirements:

### Property 1: Balance Fetch Triggers API Call

*For any* /balance command invocation, the system should call the Bybit API balance endpoint for the current mode.

**Validates: Requirements 1.1**

### Property 2: Balance Parser Extracts All Asset Types

*For any* valid Bybit API response, the balance parser should extract both USDT balance and all coin balances present in the response.

**Validates: Requirements 1.2**

### Property 3: USDT Formatting Precision

*For any* USDT amount value, the formatter should produce a string with exactly 2 decimal places and comma thousand separators.

**Validates: Requirements 1.3, 10.1**

### Property 4: Error Response Structure

*For any* API error (timeout, auth failure, rate limit, or other), the error message should contain both a descriptive error explanation and a retry button in the inline keyboard.

**Validates: Requirements 1.4, 11.1, 11.2, 11.3**

### Property 5: Mode-Based Endpoint Selection

*For any* balance fetch operation, the API session should use testnet=True when mode is DEMO and testnet=False when mode is REAL.

**Validates: Requirements 1.5, 1.6, 1.7, 15.5**

### Property 6: Mode Switch Shows Target Balance

*For any* mode switch request (DEMO→REAL or REAL→DEMO), the confirmation message should display the target mode's balance before the switch is confirmed.

**Validates: Requirements 2.1, 2.2, 2.4**

### Property 7: Low Balance Warning Threshold

*For any* REAL mode balance below $10 USDT, the mode switch confirmation should include a warning message.

**Validates: Requirements 2.3**

### Property 8: Accounts Command Fetches Both Balances

*For any* /accounts command invocation, the system should make exactly two balance API calls: one for DEMO mode and one for REAL mode.

**Validates: Requirements 3.1**

### Property 9: Balance Comparison Format

*For any* two balance values (demo and real), the comparison formatter should produce output containing both balances and an emoji marker indicating the currently active mode.

**Validates: Requirements 3.2, 3.3**

### Property 10: Partial Failure Resilience

*For any* accounts comparison where one API call fails, the system should display "unavailable" for the failed balance and still show the successful balance.

**Validates: Requirements 3.5**

### Property 11: Pre-Trade Balance Validation

*For any* trade attempt, the system should check that available balance >= (required_amount * 1.10) before proceeding, and send a warning if insufficient.

**Validates: Requirements 4.1, 4.2, 4.3**

### Property 12: Balance Cache TTL

*For any* balance fetch request, if cached data exists and is less than 30 seconds old, the cached data should be returned without making an API call.

**Validates: Requirements 4.5, 13.1, 13.2, 13.4**

### Property 13: Cache Bypass on Refresh

*For any* refresh button click, the system should bypass the cache and fetch fresh data from the API regardless of cache age.

**Validates: Requirements 13.3**

### Property 14: Cache Invalidation on Mode Switch

*For any* mode switch operation, all cached balance data should be cleared.

**Validates: Requirements 13.5**

### Property 15: File Extension Validation

*For any* uploaded file, the validator should accept only files with extensions .txt, .md, or .pdf, and reject all others.

**Validates: Requirements 5.2, 7.1**

### Property 16: File Size Limit

*For any* uploaded file with size >= 5MB, the validator should reject the file with a size error message.

**Validates: Requirements 5.3, 7.2**

### Property 17: Minimum Content Length

*For any* uploaded file with content length < 50 characters, the validator should reject the file with a content error message.

**Validates: Requirements 7.3**

### Property 18: UTF-8 Encoding Validation

*For any* text file (.txt or .md), the validator should verify the content is valid UTF-8 encoded text.

**Validates: Requirements 7.4**

### Property 19: PDF Parsing Validation

*For any* PDF file upload, the validator should attempt to parse the file with PyPDF2 and reject if parsing fails.

**Validates: Requirements 7.5**

### Property 20: Filename Sanitization

*For any* uploaded filename, the sanitizer should remove directory traversal patterns (../, ..\), convert to lowercase, and replace spaces with underscores.

**Validates: Requirements 7.7, 14.4, 14.5**

### Property 21: Upload Success Flow

*For any* file that passes validation, the system should save the file to strategies/ folder, reload the RAG system, and send a confirmation message containing filename and size.

**Validates: Requirements 5.4, 5.6, 5.7**

### Property 22: Upload Failure Messaging

*For any* file that fails validation, the error message should contain the specific validation failure reason (extension, size, content, or encoding).

**Validates: Requirements 5.5, 11.4**

### Property 23: Duplicate Filename Handling

*For any* uploaded file with a filename that already exists, the system should append a timestamp in format _YYYYMMDD_HHMMSS before the extension.

**Validates: Requirements 14.3**

### Property 24: Strategy List Completeness

*For any* /strategies command invocation, the response should include all files present in the strategies/ folder with their names and sizes in KB.

**Validates: Requirements 6.1, 6.2**

### Property 25: Strategy Preview Length

*For any* strategy file, the preview should display exactly the first 500 characters of content.

**Validates: Requirements 6.4, 12.1**

### Property 26: Preview Pagination

*For any* strategy file with content length > 500 characters, the preview should include a "Show More" button that displays the next 500 characters when clicked.

**Validates: Requirements 12.2, 12.3**

### Property 27: Delete Confirmation Flow

*For any* delete button click, the system should show a confirmation dialog before deletion, and only delete the file when confirmation is received.

**Validates: Requirements 6.5, 6.6**

### Property 28: RAG Reload Triggers Rescan

*For any* /reload_strategies command invocation, the RAG system should re-scan the strategies/ folder and reload all valid files.

**Validates: Requirements 8.1, 8.2**

### Property 29: Reload Summary Statistics

*For any* reload operation, the confirmation message should include the count of loaded strategies, total character count, and a timestamp.

**Validates: Requirements 8.3, 8.5**

### Property 30: Reload Error Reporting

*For any* reload operation where some files fail to load, the message should list each failed file with its error reason.

**Validates: Requirements 8.4**

### Property 31: Keyboard Button Layout

*For any* inline keyboard, buttons should be organized with a maximum of 2 buttons per row.

**Validates: Requirements 9.3**

### Property 32: Sub-Menu Navigation

*For any* sub-menu keyboard (mode switch, strategy preview, delete confirmation), a "Back" or "Cancel" button should be present.

**Validates: Requirements 9.5**

### Property 33: Balance Status Emoji Selection

*For any* balance value, the status emoji should be 🟢 for balance > $100, 🟡 for $10 ≤ balance ≤ $100, and 🔴 for balance < $10.

**Validates: Requirements 10.3**

### Property 34: Balance Change Percentage

*For any* balance fetch where a previous balance exists in cache, the display should include the percentage change from the previous value.

**Validates: Requirements 10.4**

### Property 35: Timestamp Format

*For any* timestamp display, the format should be HH:MM:SS (24-hour format with leading zeros).

**Validates: Requirements 10.5**

### Property 36: HTML Message Formatting

*For any* balance or strategy display message, labels should use `<b>` tags for bold and numeric values should use `<code>` tags for monospace.

**Validates: Requirements 10.6, 12.4**

### Property 37: Error Logging

*For any* error occurrence (API error, validation error, file error), an entry should be written to telegram_messages.log with timestamp and context.

**Validates: Requirements 11.5**

### Property 38: Bot Status Update

*For any* balance operation completion, the bot_status dictionary should be updated with the operation result.

**Validates: Requirements 15.6**

### Property 39: RAG Reload Integration

*For any* successful file upload or deletion, the system should call get_strategy_rag().load_strategies() to reload the RAG system.

**Validates: Requirements 15.7**


## Error Handling

### Error Categories

#### 1. Bybit API Errors

**Error Code 10001: Invalid API Key**
- **Detection**: API response with retCode=10001
- **Handling**: Display "Invalid API keys" message with setup instructions
- **Recovery**: Provide button to access /keys command
- **Logging**: Log to telegram_messages.log with full error context

**Error Code 10003: Invalid Signature**
- **Detection**: API response with retCode=10003
- **Handling**: Display "API credentials error" with re-configuration instructions
- **Recovery**: Provide button to access /keys command
- **Logging**: Log with API key prefix (first 8 chars) for debugging

**Error Code 10016: Rate Limit Exceeded**
- **Detection**: HTTP 429 or retCode=10016
- **Handling**: Return cached data if available, otherwise show "Rate limit" message
- **Recovery**: Provide retry button with exponential backoff (wait 5s, 10s, 20s)
- **Logging**: Log rate limit hit with request count

**Network Timeout**
- **Detection**: requests.Timeout exception
- **Handling**: Display "Connection timeout" message
- **Recovery**: Provide retry button, suggest checking internet connection
- **Logging**: Log timeout duration and endpoint

**Unknown API Error**
- **Detection**: Any other API error response
- **Handling**: Display error code and description from API
- **Recovery**: Provide retry button and /help command link
- **Logging**: Log full API response for debugging

#### 2. File Validation Errors

**Invalid Extension**
- **Detection**: File extension not in ['.txt', '.md', '.pdf']
- **Handling**: Display "Invalid file type" with list of supported formats
- **Recovery**: Prompt user to convert file or use supported format
- **Logging**: Log filename and attempted extension

**File Too Large**
- **Detection**: File size >= 5MB
- **Handling**: Display "File too large (X MB)" with 5MB limit
- **Recovery**: Suggest splitting file or reducing content
- **Logging**: Log filename and actual size

**Content Too Short**
- **Detection**: Content length < 50 characters
- **Handling**: Display "File content too short" with minimum requirement
- **Recovery**: Suggest adding more content
- **Logging**: Log filename and actual length

**Invalid UTF-8 Encoding**
- **Detection**: UnicodeDecodeError when reading text file
- **Handling**: Display "Invalid text encoding" with UTF-8 requirement
- **Recovery**: Suggest re-saving file as UTF-8
- **Logging**: Log filename and encoding error details

**PDF Parsing Failure**
- **Detection**: PyPDF2 exception when parsing PDF
- **Handling**: Display "Cannot parse PDF" with error details
- **Recovery**: Suggest using text format or fixing PDF
- **Logging**: Log filename and PyPDF2 error

**PyPDF2 Not Installed**
- **Detection**: ImportError when attempting PDF upload
- **Handling**: Display "PDF support not available" with installation command
- **Recovery**: Provide command: `pip install PyPDF2`
- **Logging**: Log missing dependency

#### 3. File System Errors

**Strategies Folder Missing**
- **Detection**: strategies/ folder doesn't exist
- **Handling**: Automatically create folder, log creation
- **Recovery**: Proceed with upload after creation
- **Logging**: Log folder creation

**Permission Denied**
- **Detection**: PermissionError when writing file
- **Handling**: Display "Cannot save file" with permission error
- **Recovery**: Suggest checking server permissions
- **Logging**: Log full path and permission error

**Disk Full**
- **Detection**: OSError with ENOSPC
- **Handling**: Display "Disk full" error
- **Recovery**: Suggest removing old files or contacting admin
- **Logging**: Log available disk space

**File Already Exists** (handled gracefully)
- **Detection**: File with same name exists
- **Handling**: Append timestamp to filename automatically
- **Recovery**: Save with new name, inform user of both names
- **Logging**: Log original and new filename

#### 4. Telegram API Errors

**Message Too Long**
- **Detection**: Message length > 4096 characters
- **Handling**: Split message into multiple parts
- **Recovery**: Send as multiple messages with "Part 1/N" headers
- **Logging**: Log message split count

**Invalid Chat ID**
- **Detection**: Telegram API error "chat not found"
- **Handling**: Log error, skip sending message
- **Recovery**: Verify TELEGRAM_CHAT_ID in .env
- **Logging**: Log chat ID and error

**Bot Token Invalid**
- **Detection**: Telegram API 401 Unauthorized
- **Handling**: Log critical error, disable Telegram features
- **Recovery**: Verify TELEGRAM_BOT_TOKEN in .env
- **Logging**: Log token prefix (first 8 chars)

### Error Recovery Strategies

#### Exponential Backoff

For transient errors (network, rate limits):
```python
def retry_with_backoff(func, max_retries=3):
    for attempt in range(max_retries):
        try:
            return func()
        except TransientError as e:
            if attempt == max_retries - 1:
                raise
            wait_time = 2 ** attempt  # 1s, 2s, 4s
            time.sleep(wait_time)
```

#### Graceful Degradation

When balance fetch fails:
1. Return cached data if available (even if expired)
2. Display "Last known balance" with timestamp
3. Provide refresh button to retry

When one balance fails in comparison:
1. Show "unavailable" for failed balance
2. Display successful balance normally
3. Provide retry button for failed balance only

#### User Guidance

All error messages must include:
1. **What happened**: Clear description of the error
2. **Why it happened**: Brief explanation if helpful
3. **What to do**: Actionable next steps
4. **How to get help**: Link to /help or support

Example:
```
❌ FILE UPLOAD FAILED

What: File size too large (7.2 MB)
Limit: 5 MB maximum

Next steps:
• Split file into smaller parts
• Remove unnecessary content
• Use text format instead of PDF

Need help? Type /help
```

### Logging Strategy

All errors are logged to `telegram_messages.log` with:
```json
{
    "timestamp": "2024-01-15T14:30:22",
    "level": "ERROR",
    "component": "BalanceFetcher",
    "operation": "get_balance",
    "error_type": "APIError",
    "error_code": "10016",
    "error_message": "Rate limit exceeded",
    "context": {
        "mode": "DEMO",
        "user_id": "123456789",
        "retry_count": 2
    }
}
```

## Testing Strategy

### Dual Testing Approach

This feature requires both **unit tests** and **property-based tests** for comprehensive coverage:

- **Unit tests**: Verify specific examples, edge cases, and integration points
- **Property tests**: Verify universal properties across all inputs using randomized testing

Together, these approaches ensure both concrete correctness (unit tests) and general correctness (property tests).

### Property-Based Testing

**Library**: `hypothesis` for Python

**Configuration**:
- Minimum 100 iterations per property test
- Each test tagged with comment referencing design property
- Tag format: `# Feature: telegram-control-panel-enhancement, Property {N}: {property_text}`

**Example Property Test**:
```python
from hypothesis import given, strategies as st

# Feature: telegram-control-panel-enhancement, Property 3: USDT Formatting Precision
@given(st.floats(min_value=0.0, max_value=1000000.0, allow_nan=False, allow_infinity=False))
def test_usdt_formatting_precision(amount):
    """For any USDT amount, formatter should produce exactly 2 decimal places with commas"""
    formatted = BalanceFormatter.format_currency(amount, decimals=2)
    
    # Should have exactly 2 decimal places
    assert formatted.count('.') == 1
    decimal_part = formatted.split('.')[-1]
    assert len(decimal_part) == 2
    
    # Should have comma separators for thousands
    if amount >= 1000:
        assert ',' in formatted
```

**Property Test Categories**:

1. **Formatting Properties** (Properties 3, 10, 33, 35, 36)
   - Test with random numeric values
   - Verify format structure (decimals, separators, HTML tags)

2. **Validation Properties** (Properties 15, 16, 17, 18, 20)
   - Generate random filenames and content
   - Verify accept/reject decisions

3. **Cache Properties** (Properties 12, 13, 14)
   - Generate random timestamps and modes
   - Verify cache hit/miss behavior

4. **Balance Properties** (Properties 1, 2, 5, 11)
   - Mock API responses with random data
   - Verify parsing and validation logic

5. **Flow Properties** (Properties 21, 27, 28, 39)
   - Test operation sequences
   - Verify side effects occur correctly

### Unit Testing

**Framework**: `pytest`

**Test Organization**:
```
tests/
├── test_balance_fetcher.py
├── test_balance_cache.py
├── test_balance_formatter.py
├── test_file_validator.py
├── test_strategy_uploader.py
├── test_telegram_handlers.py
├── test_keyboard_builder.py
└── test_integration.py
```

**Unit Test Focus Areas**:

1. **Specific Examples**
   - Balance of exactly $10 triggers warning
   - File of exactly 5MB is rejected
   - Cache at exactly 30 seconds is expired

2. **Edge Cases**
   - Empty balance response
   - Zero balance
   - Negative balance (error case)
   - File with no extension
   - File with multiple dots in name
   - Unicode characters in filename

3. **Integration Points**
   - get_session() called with correct testnet flag
   - get_strategy_rag() called after upload
   - bot_status updated correctly
   - Telegram API called with correct parameters

4. **Error Conditions**
   - API returns each error code (10001, 10003, 10016)
   - Network timeout occurs
   - File system errors (permission, disk full)
   - Invalid UTF-8 encoding
   - PDF parsing failure

**Example Unit Test**:
```python
def test_low_balance_warning_at_threshold():
    """Test that exactly $10 balance triggers warning"""
    balance = BalanceData(
        total_equity=10.0,
        available_balance=10.0,
        usdt_balance=10.0,
        coin_balances={},
        timestamp=datetime.now(),
        mode="REAL"
    )
    
    message = BalanceFormatter.format_display(balance)
    
    # Should include warning for REAL mode at $10
    assert "⚠️" in message or "warning" in message.lower()
```

### Mock Strategy

**Bybit API Mocking**:
```python
@pytest.fixture
def mock_bybit_session(mocker):
    """Mock Bybit API session"""
    mock_session = mocker.Mock()
    mock_session.get_wallet_balance.return_value = {
        "retCode": 0,
        "retMsg": "OK",
        "result": {
            "list": [{
                "totalEquity": "1000.50",
                "totalAvailableBalance": "950.25",
                "coin": [{
                    "coin": "USDT",
                    "walletBalance": "1000.50",
                    "availableToWithdraw": "950.25"
                }]
            }]
        }
    }
    mocker.patch('trader.get_session', return_value=mock_session)
    return mock_session
```

**Telegram API Mocking**:
```python
@pytest.fixture
def mock_telegram_api(mocker):
    """Mock Telegram API calls"""
    mock_post = mocker.patch('requests.post')
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {"ok": True}
    return mock_post
```

**File System Mocking**:
```python
@pytest.fixture
def mock_strategies_folder(tmp_path):
    """Create temporary strategies folder"""
    strategies_dir = tmp_path / "strategies"
    strategies_dir.mkdir()
    return strategies_dir
```

### Test Coverage Goals

- **Line Coverage**: > 90%
- **Branch Coverage**: > 85%
- **Property Tests**: All 39 properties implemented
- **Unit Tests**: Minimum 3 tests per component
- **Integration Tests**: All command flows tested end-to-end

### Continuous Testing

**Pre-commit Hooks**:
- Run unit tests on changed files
- Run property tests with 10 iterations (fast check)

**CI Pipeline**:
- Run full unit test suite
- Run property tests with 100 iterations
- Generate coverage report
- Fail if coverage drops below threshold

**Manual Testing Checklist**:
- [ ] /balance command in DEMO mode
- [ ] /balance command in REAL mode
- [ ] /accounts comparison
- [ ] Mode switch with balance display
- [ ] Upload .txt file
- [ ] Upload .md file
- [ ] Upload .pdf file (if PyPDF2 installed)
- [ ] Upload invalid file (wrong extension)
- [ ] Upload oversized file (> 5MB)
- [ ] /strategies list
- [ ] Strategy preview
- [ ] Strategy delete with confirmation
- [ ] /reload_strategies command
- [ ] Balance refresh button
- [ ] Cache behavior (fetch twice within 30s)
- [ ] Error handling (disconnect network, test timeout)
- [ ] Rate limit handling (make many rapid requests)

