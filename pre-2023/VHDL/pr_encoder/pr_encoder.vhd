----------------------------------------------------------------------------------
-- Company: Stevens Institute of Technology
-- Engineer: Alexander Buchholz
-- 
-- Create Date:    20:17:21 02/11/2017 
-- Design Name: 
-- Module Name:    pr_encoder - Behavioral 
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
entity pr_encoder is
port(S0,S1,S2,S3: in std_logic;
	Z: out std_logic_vector (1 downto 0));
end entity pr_encoder;

architecture dataflow of pr_encoder is
begin
	encoder_proc : process (S0, S1, S2, S3)
	begin
		if S2 = '1' then
			Z <= "10" after 5ns;
		elsif S3 = '1' then
			Z <= "11" after 5ns;
		elsif S1 = '1' then
			Z <= "01" after 5ns;
		elsif S0 = '1' then
			Z <= "00" after 5ns;
		--else
			--Z <= "00" after 5ns;
		end if;
	end process encoder_proc;
end architecture dataflow;
