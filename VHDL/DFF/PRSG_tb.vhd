--------------------------------------------------------------------------------
-- Company: 
-- Engineer:
--
-- Create Date:   08:14:37 02/13/2017
-- Design Name:   
-- Module Name:   C:/Users/buchha2/Desktop/code/VHDL/DFF/PRSG_tb.vhd
-- Project Name:  DFF
-- Target Device:  
-- Tool versions:  
-- Description:   
-- 
-- VHDL Test Bench Created by ISE for module: PRSG
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
 
ENTITY PRSG_tb IS
END PRSG_tb;
 
ARCHITECTURE behavior OF PRSG_tb IS 
 
    -- Component Declaration for the Unit Under Test (UUT)
 
    COMPONENT PRSG
    PORT(
         clk : IN  std_logic;
         reset : IN  std_logic;
         data : INOUT  std_logic_vector(3 downto 0)
        );
    END COMPONENT;
    

   --Inputs
   signal clk : std_logic := '0';
   signal reset : std_logic := '0';

 	--Outputs
   signal data : std_logic_vector(3 downto 0);

   -- Clock period definitions
   constant clk_period : time := 50 ns;
 
BEGIN
 
	-- Instantiate the Unit Under Test (UUT)
   uut: PRSG PORT MAP (
          clk => clk,
          reset => reset,
          data => data
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
	
	PRSG_proc: process
	begin
		wait for 20 ns;
		reset <= '1';		
		wait for 250 ns;
		reset <= '0';
		wait;
	end process;

END;
