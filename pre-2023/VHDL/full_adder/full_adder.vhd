----------------------------------------------------------------------------------
-- Company: Stevens Institute of Technology
-- Engineer: Alexander Buchholz
-- 
-- Create Date:    21:35:14 02/04/2017 
-- Design Name: Full Adder Tutorial
-- Module Name:    full_adder - gate_level 
-- Project Name: full_adder
-- Target Devices: 
-- Tool versions: 
-- Description: Homework 1 of CPE 690, implementation of a full adder in VHDL
--
-- Dependencies: 
--
-- Revision: 
-- Revision 0.01 - File Created
-- Additional Comments: 
--
----------------------------------------------------------------------------------
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity full_adder is
	Port ( a : in STD_LOGIC;
			b : in STD_LOGIC;
			cin : in STD_LOGIC;
			sum : out STD_LOGIC;
			cout : out STD_LOGIC);
end full_adder;

architecture gate_level of full_adder is
signal s1,s2,s3:std_logic;
begin
	cout <= s2 or s3 after 3 ns;
	sum <= (s1 xor cin) after 5 ns;
	s3 <= (a and b) after 3 ns;
	s2 <= (cin and s1) after 3 ns;
	s1 <= (a xor b) after 5 ns;

end gate_level;

