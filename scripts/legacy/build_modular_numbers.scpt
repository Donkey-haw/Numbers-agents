tell application "Numbers"
    activate
    
    set targetFile to POSIX file "/Users/jonyeock/Desktop/Tool/NumbersAuto/완벽_빈_템플릿.numbers"
    open targetFile
    delay 1 
    
    set myDoc to document 1
    
    tell active sheet of myDoc
        try
            delete every table
        end try
        try
            delete every text item
        end try
        try
            delete every shape
        end try
        try
            delete every image
        end try
        
        set keywordTable to make new table with properties {name:"핵심 단어", row count:5, column count:2}
        tell keywordTable
            set position to {420, 320}
            set value of cell "A1" to "단어 목록"
        end tell
        
        set summaryTable to make new table with properties {name:"내용 요약 및 활동", row count:5, column count:2}
        tell summaryTable
            set position to {590, 320}
            set value of cell "A1" to "구분"
            set value of cell "B1" to "활동 내용"
        end tell
    end tell
    save myDoc
end tell
