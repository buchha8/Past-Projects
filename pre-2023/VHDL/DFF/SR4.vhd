----------------------------------------------------------------------------------
-- Company: 
-- Engineer: 
-- 
-- Create Date:    03:10:42 02/13/2017 
-- Design Name: 
-- Module Name:    SR4 - Behavioral 
-- Project Name: 
-- Target Devices: 
-- Tool versions: 
-- Description: 
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

entity SR4 is
    Port ( sin : in  STD_LOGIC;
           clk : in  STD_LOGIC;
			  --Q0 to Q2 declared as inout, node can be used as SR4 output and input to next flipflop
           Q0 : inout  STD_LOGIC;
           Q1 : inout  STD_LOGIC;
           Q2 : inout  STD_LOGIC;
           Q3 : out  STD_LOGIC);
end SR4;

architecture structural of SR4 is
component DFF
	port(D, clk: in std_logic;
	Q, Qb: out std_logic);
end component;

begin
	Inst0: DFF port map(D=>sin, clk=>clk, Q=>Q0, Qb=>open);
	Inst1: DFF port map(D=>Q0, clk=>clk, Q=>Q1, Qb=>open);
	Inst2: DFF port map(D=>Q1, clk=>clk, Q=>Q2, Qb=>open);
	Inst3: DFF port map(D=>Q2, clk=>clk, Q=>Q3, Qb=>open);

end architecture structural;

