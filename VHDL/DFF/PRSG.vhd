----------------------------------------------------------------------------------
-- Company: Stevens Institute of Technology
-- Engineer: Alexander Buchholz
-- 
-- Create Date:    07:52:10 02/13/2017 
-- Design Name: 
-- Module Name:    PRSG - Behavioral 
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

entity PRSG is
    Port ( clk : in  STD_LOGIC;
           reset : in  STD_LOGIC;
			  --data inout because we made Q0-Q2 inouts
           data : inout STD_LOGIC_VECTOR(3 downto 0));
end PRSG;

architecture structural of PRSG is
component SR4
    Port ( sin : in  STD_LOGIC;
           clk : in  STD_LOGIC;
			  --Q0 to Q2 declared as inout, node can be used as SR4 output and input to next flipflop
           Q0 : inout  STD_LOGIC;
           Q1 : inout  STD_LOGIC;
           Q2 : inout  STD_LOGIC;
           Q3 : out  STD_LOGIC);
end component;

signal xor_out, or_out: std_logic;

begin
	xor_out <= data(2) xor data(3);
	or_out <= xor_out or reset;
	Inst0: SR4 port map(sin=>or_out, clk=>clk, Q0=>data(0), Q1=>data(1), Q2=>data(2), Q3=>data(3));

end architecture structural;

