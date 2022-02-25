--------------------------------------------------------------------------------
-- Company: Stevens Institute of Technology
-- Engineer: Alexander Buchholz
--
-- Create Date:   04:27:56 02/12/2017
-- Design Name:   
-- Module Name:   C:/Users/buchha2/Desktop/code/VHDL/DFF/DFF_tb.vhd
-- Project Name:  DFF
-- Target Device:  
-- Tool versions:  
-- Description:   
-- 
-- VHDL Test Bench Created by ISE for module: DFF
-- 
-- Dependencies:
-- 
-- Revision:
-- Revision 0.01 - File Created
-- Additional Comments:
--
-- Notes: 
-- This testbench has been automatically generated using types std_logic and
-- std_logic_vector for the ports of the unit under test.  Xilinx recommends
-- that these types always be used for the top-level I/O of a design in order
-- to guarantee that the testbench will bind correctly to the post-implementation 
-- simulation model.
--------------------------------------------------------------------------------
LIBRARY ieee;
USE ieee.std_logic_1164.ALL;
 
-- Uncomment the following library declaration if using
-- arithmetic functions with Signed or Unsigned values
--USE ieee.numeric_std.ALL;
 
ENTITY DFF_tb IS
END DFF_tb;
 
ARCHITECTURE behavior OF DFF_tb IS 
 
    -- Component Declaration for the Unit Under Test (UUT)
 
    COMPONENT DFF
    PORT(
         D : IN  std_logic;
         clk : IN  std_logic;
         Q : OUT  std_logic;
         Qb : OUT  std_logic
        );
    END COMPONENT;
    

   --Inputs
   signal D : std_logic := '0';
   signal clk : std_logic := '0';

 	--Outputs
   signal Q : std_logic;
   signal Qb : std_logic;

   -- Clock period definitions
   constant clk_period : time := 100 ns;
 
BEGIN
 
	-- Instantiate the Unit Under Test (UUT)
   uut: DFF PORT MAP (
          D => D,
          clk => clk,
          Q => Q,
          Qb => Qb
        );

   -- Clock process definitions
   clk_process :process
   begin
		clk <= '0';
		wait for clk_period/2;
		clk <= '1';
		wait for clk_period/2;
   end process;
 

   -- Stimulus process
   stim_proc: process
   begin		
      -- hold reset state for 100 ns.
      wait for 100 ns;	

      wait for clk_period*10;

      -- insert stimulus here 

      wait;
   end process;

	D_proc: process
	begin
		wait for 70 ns;
		D <= '1';
		
		wait for 100 ns;
		D <= '0';

	
	end process;
END;
