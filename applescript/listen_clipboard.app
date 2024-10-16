on idle
    set clipboardContent to (the clipboard as text)
    if clipboardContent is not equal to last_clipboard then
    
        set last_clipboard to clipboardContent
        
        -- Call Python script for LLM processing
        set processedText to do shell script "python3  /Users/flybywindwen/Projects/llm-wechat/echo.py" & quoted form of clipboardContent
        
        tell application "System Events"
            keystroke processedText
        end tell
    end if
    return 1
end idle

on run
    set last_clipboard to ""
    return
end run