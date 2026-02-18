%NASA/JPL CubeSat SADA (2) RPI Capstone Project: Spring 2016
%5/15/2016
%Code used for LTR-4206E analysis
%This code plots the information listed on the LTR-4206E datasheet

%Define sensor ranges for 20 degree offset
theta1 = -50 : 2.5 : 10;
theta2 = -30 : 2.5 : 30;
theta3 = -10 : 2.5 : 50;

%Values taken from LTR-4206E datasheet
sensitivity = [0.05, 0.06, 0.07, 0.08, 0.1, 0.15, 0.2, 0.35, 0.53, ...
    0.68, 0.87, 0.97, 1, 0.97, 0.87, 0.68, 0.53, 0.35, 0.2, 0.15, 0.1, ...
    0.08, 0.07, 0.06, 0.05];

%Plot first figure
plot(theta1,sensitivity,'color','r'); hold on;
plot(theta2,sensitivity,'color','g'); hold on;
plot(theta3,sensitivity,'color','b');

%Figure Labels
title('Sensitivity with 20 Degree Offset');
xlabel('Angle from Centerline (Degrees)');
ylabel('Normalized Sensitivity');

%Define sensor ranges for 15 degree offset
theta4 = -45 : 2.5 : 15;
theta5 = -30 : 2.5 : 30;
theta6 = -15 : 2.5 : 45;

%Plot second figure
figure();
plot(theta4,sensitivity,'color','r'); hold on;
plot(theta5,sensitivity,'color','g'); hold on;
plot(theta6,sensitivity,'color','b');

%Figure Labels
title('Sensitivity with 15 Degree Offset');
xlabel('Angle from Centerline (Degrees)');
ylabel('Normalized Sensitivity');