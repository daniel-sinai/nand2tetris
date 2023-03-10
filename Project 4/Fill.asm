// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

// Put your code here.




(LISTENER)
	//init pixel = SCREEN
	@SCREEN
	D = A
	@pixel
	M = D
	//if (KBD != 0) goto BLACK
	@KBD
	D = M
	@BLACK
	D;JNE
	//goto WHITE
	@WHITE
	0,JMP
	
(BLACK)
	//set color black
	@color
	M = -1
	@PAINT
	0;JMP
	
(WHITE)
	//set color WHITE
	@color
	M = 0
	@PAINT
	0;JMP
	
(PAINT)
	//if the pixel val is KBD goto LISTENER
	@pixel
	D = M
	@KBD
	D = D - A
	@LISTENER
	D;JGE
	//paint cur pixel
	@color
	D = M
	@pixel
	A = M
	M = D
	//advance pixel
	@pixel
	M = M + 1
	//repeat PAINT
	@PAINT
	0;JMP




	
	