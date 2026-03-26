set projectPath to "/Users/jonyeock/Desktop/Tool/NumbersAuto"
set sourceFile to POSIX file (projectPath & "/output/6-1-2. 민주화와 산업화로 달라진 생활 문화.numbers")

set sheetNames to {"7차시", "8-9차시", "10차시", "11차시", "12-13차시"}
set imageNames to {"unit2_7차시.png", "unit2_8-9차시.png", "unit2_10차시.png", "unit2_11차시.png", "unit2_12-13차시.png"}

tell application "Numbers"
	activate
	open sourceFile
	delay 2
	
	set myDoc to document 1
	
	repeat with i from 1 to count of sheetNames
		set targetSheetName to item i of sheetNames
		set imagePath to projectPath & "/assets/cards/" & item i of imageNames
		
		if i is 1 then
			tell sheet 1 of myDoc
				set name to targetSheetName
			end tell
			set targetSheet to sheet 1 of myDoc
		else
			tell myDoc
				set targetSheet to make new sheet with properties {name:targetSheetName}
			end tell
		end if
		
		tell targetSheet
			try
				delete every table
			end try
			try
				delete every image
			end try
			try
				delete every text item
			end try
			try
				delete every shape
			end try
			
			set cardImage to make new image with properties {file:POSIX file imagePath}
			set position of cardImage to {20, 20}
			set width of cardImage to 980
		end tell
	end repeat
	
	save myDoc
	close myDoc
end tell
