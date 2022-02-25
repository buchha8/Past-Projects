--------------------------------------------------------------------------------
-- Company: 
-- Engineer:
--
-- Create Date:   04:18:45 02/13/2017
-- Design Name:   
-- Module Name:   C:/Users/buchha2/Desktop/code/VHDL/DFF/SR4_tb.vhd
-- Project Name:  DFF
-- Target Device:  
-- Tool versions:  
-- Description:   
-- 
-- VHDL Test Bench Created by ISE for module: SR4
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
 
ENTITY SR4_tb IS
END SR4_tb;
 
ARCHITECTURE behavior OF SR4_tb IS 
 
    -- Component Declaration for the Unit Under Test (UUT)
 
    COMPONENT SR4
    PORT(
         sin : IN  std_logic;
         clk : IN  std_logic;
         Q0 : INOUT  std_logic;
         Q1 : INOUT  std_logic;
         Q2 : INOUT  std_logic;
         Q3 : OUT  std_logic
        );
    END COMPONENT;

   --Inputs
   signal sin : std_logic := '0';
   signal clk : std_logic := '0';

	--BiDirs
   signal Q0 : std_logic;
   signal Q1 : std_logic;
   signal Q2 : std_logic;

 	--Outputs
   signal Q3 : std_logic;

   -- Clock period definitions
   constant clk_period : time := 50 ns;
 
BEGIN
 
	-- Instantiate the Unit Under Test (UUT)
   uut: SR4 PORT MAP (
          sin => sin,
          clk => clk,
          Q0 => Q0,
          Q1 => Q1,
          Q2 => Q2,
          Q3 => Q3
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

	SR4_proc: process
	begin
		wait for 210 ns;
		sin <= '1';		
		wait for 200 ns;
		sin <= '0';
		wait;
	end process;
	
END;
