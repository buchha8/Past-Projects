--------------------------------------------------------------------------------
-- Company: Stevens Institute of Technology
-- Engineer: Alexander Buchholz
--
-- Create Date:   20:18:03 02/11/2017
-- Design Name:   
-- Module Name:   C:/Users/buchha2/Desktop/code/VHDL/pr_encoder/pr_encoder_tb.vhd
-- Project Name:  pr_encoder
-- Target Device:  
-- Tool versions:  
-- Description:   
-- 
-- VHDL Test Bench Created by ISE for module: pr_encoder
-- 
-- Dependencies:
-- 
-- Revision:
-- Revision 0.01 - File Created
-- Additional Comments:
--------------------------------------------------------------------------------
LIBRARY ieee;
USE ieee.std_logic_1164.ALL;
 
ENTITY pr_encoder_tb IS
END pr_encoder_tb;
 
ARCHITECTURE behavior OF pr_encoder_tb IS 
 
    -- Component Declaration for the Unit Under Test (UUT)
 
    COMPONENT pr_encoder
    PORT(
         S0 : IN  std_logic;
         S1 : IN  std_logic;
         S2 : IN  std_logic;
         S3 : IN  std_logic;
         Z : OUT  std_logic_vector(1 downto 0));
    END COMPONENT;

   --Inputs, default uninitialized
   signal S0 : std_logic := 'U';
   signal S1 : std_logic := 'U';
   signal S2 : std_logic := 'U';
   signal S3 : std_logic := 'U';

 	--Outputs, default uninitialized
   signal Z : std_logic_vector(1 downto 0) := "UU";
 
BEGIN
 
	-- Instantiate the Unit Under Test (UUT)
   uut: pr_encoder PORT MAP (
          S0 => S0,
          S1 => S1,
          S2 => S2,
          S3 => S3,
          Z => Z
        );

TB: process
	constant PERIOD: time :=20ns;
	BEGIN
	--first wait to test uninitialized case
		wait for PERIOD;
		S0<='0'; S1<='0'; S2<='0'; S3<='0';
		wait for PERIOD;
		S0<='0'; S1<='0'; S2<='0'; S3<='1';
		wait for PERIOD;
		S0<='0'; S1<='0'; S2<='1'; S3<='0';
		wait for PERIOD;
		S0<='0'; S1<='0'; S2<='1'; S3<='1';
		wait for PERIOD;
		S0<='0'; S1<='1'; S2<='0'; S3<='0';
		wait for PERIOD;
		S0<='0'; S1<='1'; S2<='0'; S3<='1';
		wait for PERIOD;
		S0<='0'; S1<='1'; S2<='1'; S3<='0';
		wait for PERIOD;
		S0<='0'; S1<='1'; S2<='1'; S3<='1';
		wait for PERIOD;
		S0<='1'; S1<='0'; S2<='0'; S3<='0';
		wait for PERIOD;
		S0<='1'; S1<='0'; S2<='0'; S3<='1';
		wait for PERIOD;
		S0<='1'; S1<='0'; S2<='1'; S3<='0';
		wait for PERIOD;
		S0<='1'; S1<='0'; S2<='1'; S3<='1';
		wait for PERIOD;
		S0<='1'; S1<='1'; S2<='0'; S3<='0';
		wait for PERIOD;
		S0<='1'; S1<='1'; S2<='0'; S3<='1';
		wait for PERIOD;
		S0<='1'; S1<='1'; S2<='1'; S3<='0';
		wait for PERIOD;
		S0<='1'; S1<='1'; S2<='1'; S3<='1';
		wait;
	END process;
END;
