// This file is part of nand2tetris, as taught in The Hebrew University, and
// was written by Aviv Yaish. It is an extension to the specifications given
// [here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
// as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
// Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).

// The program should swap between the max. and min. elements of an array.
// Assumptions:
// - The array's start address is stored in R14, and R15 contains its length
// - Each array value x is between -16384 < x < 16384
// - The address in R14 is at least >= 2048
// - R14 + R15 <= 16383
//
// Requirements:
// - Changing R14, R15 is not allowed.

// save pointers to min and max locations in the array
@R14
D=M
@P_MIN
M=D
@P_MAX
M=D

// initialize min and max to the default
@R14
A=M
D=M
@MIN_VAL
M=D
@MAX_VAL
M=D

@i
M=0

(LOOP_START)
	// check if loop needs to end
	@i
	D=M
	@R15
	D=M-D
	@LOOP_END
	D;JEQ
	
	// check min
	@R14
	D=M
	@i
	D=D+M
	
	// save arr[i] address in temp location
	@temp_address
	M=D
	
	// get arr[i]
	A=D
	D=M
	
	// save arr[i] in temp location
	@temp_val
	M=D
	
	@MIN_VAL
	D=D-M
	@MAX_SWAP
	D;JGT
	
	// swap between arr[i] and MIN_VAL
	@temp_val
	D=M
	@MIN_VAL
	M=D
	
	// swap addresses of arr[i] and current P_MIN
	@temp_address
	D=M
	@P_MIN
	M=D
	
	(MAX_SWAP)
	// check max
	@R14
	D=M
	@i
	D=D+M
	
	// save arr[i] address in temp location
	@temp_address
	M=D
	
	// get arr[i]
	A=D
	D=M
	
	// save arr[i] in temp location
	@temp_val
	M=D
	
	@MAX_VAL
	D=D-M
	@INCREMENTOR
	D;JLT
	
	// swap between arr[i] and MAX_VAL
	@temp_val
	D=M
	@MAX_VAL
	M=D
	
	// swap addresses of arr[i] and current P_MAX
	@temp_address
	D=M
	@P_MAX
	M=D

// increment i by one and start the loop again	
(INCREMENTOR)
@i
M=M+1
@LOOP_START
0;JMP

// finish loop and swap between min and max
(LOOP_END)
@MIN_VAL
D=M
@P_MAX
A=M
M=D

@MAX_VAL
D=M
@P_MIN
A=M
M=D

(INFINITE_LOOP)
@INFINITE_LOOP
0;JMP