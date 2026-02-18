----------------------------------------------------------------------------------
-- Company: Stevens Institute of Technology
-- Engineer: Alexander Buchholz
-- 
-- Create Date:    06:57:17 02/13/2017 
-- Design Name: 
-- Module Name:    SequenceFSM - Behavioral 
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

entity SequenceFSM is
    Port ( data_in : in  STD_LOGIC;
           clk : in  STD_LOGIC;
           reset : in  STD_LOGIC;
           data_out : out  STD_LOGIC);
end SequenceFSM;

architecture mealy of SequenceFSM is
type state is (stateA, stateB, stateC, stateD);
signal pr_state, nx_state : state;
begin

--clk process taken from Lecture 4 slides, Toggle Multiplexer example
p_clk: process (reset, clk)
	begin
		if(reset = '1') then
			pr_state<= stateA;
		elsif(clk'event and clk = '1') then
			pr_state<= nx_state;
		end if;
	end process;
	
p_comb: process(data_in, pr_state)
	begin
		case pr_state is
		when stateA=>
			--set data_out to 0 until sequence is detected
			data_out<='0';
			if(data_in='1') then nx_state<=stateB;
				else nx_state <= stateA;
			end if;
		when stateB=>
			if(data_in='0') then nx_state<=stateC;
				else nx_state <= stateB;
			end if;
		when stateC=>
			if(data_in='1') then nx_state<=stateD;
				else nx_state <= stateA;
			end if;
		when stateD=>
			if(data_in='1') then
				--sequence detected, set data_out to 1 for this bit
				data_out <= '1';
				nx_state<=stateA;
				else nx_state <= stateA;
			end if;
		end case;
	end process;
end architecture mealy;

