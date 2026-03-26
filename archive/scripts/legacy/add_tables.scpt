set projectPath to "/Users/jonyeock/Desktop/Tool/NumbersAuto"
set outputFile to POSIX file (projectPath & "/output/6학년_1학기_사회_1단원_평화통일.numbers")

tell application "Numbers"
	activate
	
	-- Open the generated file
	open outputFile
	delay 1
	set myDoc to document 1
	
	set sheetNames to {"Lesson1", "Lesson2", "Lesson3", "Lesson4"}
	
	repeat with sName in sheetNames
		tell sheet (sName as string) of myDoc
			-- Create a default table (usually 5x5) and just position it
			set keywordTable to make new table with properties {name:"핵심 단어"}
			tell keywordTable
				set position to {435, 305}
				set value of cell "A1" to "핵심 단어"
			end tell
			
			set summaryTable to make new table with properties {name:"내용 요약 및 활동"}
			tell summaryTable
				set position to {435, 555}
				set value of cell "A1" to "구분"
				set value of cell "B1" to "활동 및 요약"
			end tell
		end tell
	end repeat
	
	save myDoc
end tell
