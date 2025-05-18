======================================
Sudoku Solver for Windows
======================================

[Overview]
This application is a tool for solving Sudoku puzzles and generating new ones.
Sudoku is a logic puzzle where you fill a 9x9 grid with numbers from 1 to 9, ensuring
that each row, column, and 3x3 block contains no duplicate numbers.

[How to Use]
1. Starting the Application
   Double-click sudoku_solver.exe to launch the application.

2. Main Features
   - "Load": Open a saved Sudoku file (.txt)
   - "Generate": Create a new Sudoku puzzle (you can select difficulty)
   - "Solve": Automatically solve the current board
   - "Reset": Return the board to its initial state
   - "Save": Save the current board as a .txt file
   - "Exit": Close the application

3. Entering Numbers
   - Click on an empty cell to select it, then enter a number from 1 to 9
   - To clear a number, press 0 or Delete
   - Use arrow keys to move between cells

4. Solving the Board
   - Click the "Solve" button to start the automatic solving process
   - During solving, the "Solve" button changes to "Stop"
   - Adjust the solving speed using the slider (left is slower, right is faster)

5. Sample Files
   You can try sample puzzles by opening the included files: sample_easy.txt,
   sample_medium.txt, and sample_hard.txt using the "Load" button.

6. Language Settings
   - The application supports Japanese and English languages
   - There are two ways to change the language:
     a) Open the ui_setting.json file with a text editor and change the "language" value to "ja" (Japanese) or "en" (English)
     b) Launch from Command Prompt or PowerShell:
        Command Prompt: start "" "sudoku_solver.exe" --language en
        PowerShell: Start-Process -FilePath "sudoku_solver.exe" -ArgumentList "--language en"

[Notes]
- Boards with rule violations (same number in the same row/column/block) cannot be solved
- If a puzzle has no solution, a message will be displayed
- Large or complex puzzles may take more time to solve

[Troubleshooting]
If the application fails to start, please check the following:
1. Ensure Windows Defender or other security software is not blocking it
2. Verify you have the necessary permissions to run the application
3. Check that your PC meets the minimum requirements

====================================== 