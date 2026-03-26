set projectPath to "/Users/jonyeock/Desktop/Tool/NumbersAuto"
set templateFile to POSIX file (projectPath & "/빈 넘버스 파일.numbers")
set outputFile to POSIX file (projectPath & "/output/6학년_1학기_사회_1단원_평화통일.numbers")

tell application "Numbers"
	activate
	
	-- Open template
	open templateFile
	delay 2
	set myDoc to document 1
	
	-- Lesson Data
	set lessonTitles to {"Lesson1", "Lesson2", "Lesson3", "Lesson4"}
	set cardNames to {"lesson_1.png", "lesson_2.png", "lesson_3.png", "lesson_4.png"}
	
	-- Create Sheets for each lesson
	repeat with i from 1 to count of lessonTitles
		set lessonTitle to item i of lessonTitles
		set cardName to item i of cardNames
		set cardPath to (projectPath & "/assets/cards/" & cardName)
		
		tell myDoc
			set newSheet to make new sheet with properties {name:lessonTitle}
			tell newSheet
				-- Delete default tables
				delete every table
				
				-- 1. Insert Background Card
				set bgImg to make new image with properties {file:POSIX file cardPath}
				set position of bgImg to {0, 0}
				set width of bgImg to 960
				set height of bgImg to 540
			end tell
		end tell
	end repeat
	
	-- Delete the first empty sheet
	try
		delete sheet 1 of myDoc
	end try
	
	-- Save as new file
	save myDoc in outputFile
end tell
