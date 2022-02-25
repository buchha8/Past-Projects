----------------------------------------------------------------------------------
-- Company: Stevens Institute of Technology
-- Engineer: Alexander Buchholz
-- 
-- Create Date:    03:59:53 02/12/2017 
-- Design Name: 
-- Module Name:    DFF - Behavioral 
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
use IEEE.std_logic_1164.all;
entity DFF is
port(D, clk: in std_logic;
	Q, Qb: out std_logic);
end entity DFF;

architecture behavioral of DFF is
begin
ffpr: process is
	begin
		wait until clk'event and clk='1';
		Q <= D after 10ns;
		Qb <= not D after 10 ns;
	end process;
end behavioral;

