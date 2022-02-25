%Initialize Data, Alexander Buchholz
%This file contains all preliminary image parsing and pre-processing

disp('Pre-processing start');
clear;
%Grab system account name so file path does not change on other computers
username = getenv('username');
filePath = strcat('C:\Users\',username,'\Documents\MATLAB\Bird_Classifier\birds_training\egret\');
imList=dir(fullfile(filePath,'*.jpg'));
numFiles= size(imList,1);

%PREPAD_SIZE and SCALE can be edited to change the properties of input
%vector X
PREPAD_SIZE=900;
SCALE=.1;

%Initialization. Note that all image values must be stored as floating points for the
%matrix operations performed in Bird_Classifier.m
egretX=zeros(PREPAD_SIZE*SCALE,PREPAD_SIZE*SCALE,numFiles,'double');
mandarinX=zeros(PREPAD_SIZE*SCALE,PREPAD_SIZE*SCALE,numFiles,'double');
owlX=zeros(PREPAD_SIZE*SCALE,PREPAD_SIZE*SCALE,numFiles,'double');
puffinX=zeros(PREPAD_SIZE*SCALE,PREPAD_SIZE*SCALE,numFiles,'double');
toucanX=zeros(PREPAD_SIZE*SCALE,PREPAD_SIZE*SCALE,numFiles,'double');
wood_duckX=zeros(PREPAD_SIZE*SCALE,PREPAD_SIZE*SCALE,numFiles,'double');



%begin assembling data for training images
%Add padding, scale, and store pre-processed image. If uneven padding is
%required, add extra row/column after the scaled image
for i = 1:numFiles
    im = imread([filePath,imList(i).name]);
    [rows, columns, colors] = size(im);
   
    A= padarray(im, [floor((PREPAD_SIZE-rows)/2) floor((PREPAD_SIZE-columns)/2)], 'replicate', 'pre');
    A = padarray(A, [ceil((PREPAD_SIZE-rows)/2) ceil((PREPAD_SIZE-columns)/2)], 'replicate', 'post');
    egretX(:,:,i)= im2double(rgb2gray(imresize(A,SCALE)));
end

filePath = strcat('C:\Users\',username,'\Documents\MATLAB\Bird_Classifier\birds_training\mandarin\');
imList=dir(fullfile(filePath,'*.jpg'));
for i = 1:numFiles
    im = imread([filePath,imList(i).name]);
    [rows, columns, colors] = size(im);
    
    A= padarray(im, [floor((PREPAD_SIZE-rows)/2) floor((PREPAD_SIZE-columns)/2)], 'replicate', 'pre');
    A= padarray(A, [ceil((PREPAD_SIZE-rows)/2) ceil((PREPAD_SIZE-columns)/2)], 'replicate', 'post');
    mandarinX(:,:,i)= im2double(rgb2gray(imresize(A,SCALE)));
end

filePath = strcat('C:\Users\',username,'\Documents\MATLAB\Bird_Classifier\birds_training\owl\');
imList=dir(fullfile(filePath,'*.jpg'));
for i = 1:numFiles
    im = imread([filePath,imList(i).name]);
    [rows, columns, colors] = size(im);
    
    A= padarray(im, [floor((PREPAD_SIZE-rows)/2) floor((PREPAD_SIZE-columns)/2)], 'replicate', 'pre');
    A= padarray(A, [ceil((PREPAD_SIZE-rows)/2) ceil((PREPAD_SIZE-columns)/2)], 'replicate', 'post');
    owlX(:,:,i)= im2double(rgb2gray(imresize(A,SCALE)));
end

filePath = strcat('C:\Users\',username,'\Documents\MATLAB\Bird_Classifier\birds_training\puffin\');
imList=dir(fullfile(filePath,'*.jpg'));
for i = 1:numFiles
    im = imread([filePath,imList(i).name]);
    [rows, columns, colors] = size(im);
    
    A= padarray(im, [floor((PREPAD_SIZE-rows)/2) floor((PREPAD_SIZE-columns)/2)], 'replicate', 'pre');
    A= padarray(A, [ceil((PREPAD_SIZE-rows)/2) ceil((PREPAD_SIZE-columns)/2)], 'replicate', 'post');
    puffinX(:,:,i)= im2double(rgb2gray(imresize(A,SCALE)));
end

filePath = strcat('C:\Users\',username,'\Documents\MATLAB\Bird_Classifier\birds_training\toucan\');
imList=dir(fullfile(filePath,'*.jpg'));
for i = 1:numFiles
    im = imread([filePath,imList(i).name]);
    [rows, columns, colors] = size(im);
    
    A= padarray(im, [floor((PREPAD_SIZE-rows)/2) floor((PREPAD_SIZE-columns)/2)], 'replicate', 'pre');
    A= padarray(A, [ceil((PREPAD_SIZE-rows)/2) ceil((PREPAD_SIZE-columns)/2)], 'replicate', 'post');
    toucanX(:,:,i)= im2double(rgb2gray(imresize(A,SCALE)));
end

filePath = strcat('C:\Users\',username,'\Documents\MATLAB\Bird_Classifier\birds_training\wood_duck\');
imList=dir(fullfile(filePath,'*.jpg'));
for i = 1:numFiles
    im = imread([filePath,imList(i).name]);
    [rows, columns, colors] = size(im);
    
    A= padarray(im, [floor((PREPAD_SIZE-rows)/2) floor((PREPAD_SIZE-columns)/2)], 'replicate', 'pre');
    A= padarray(A, [ceil((PREPAD_SIZE-rows)/2) ceil((PREPAD_SIZE-columns)/2)], 'replicate', 'post');
    wood_duckX(:,:,i)= im2double(rgb2gray(imresize(A,SCALE)));
end

disp('Training images compiled');
%begin compiling data for test images

%The second half of the file performs the same exact operations for the
%test matrices.
%Also store the original images, so that they can be written to directories
%after classification

filePath = strcat('C:\Users\',username,'\Documents\MATLAB\Bird_Classifier\birds_testing\egret\');
imList=dir(fullfile(filePath,'*.jpg'));
numFiles= size(imList,1);

egretTest=zeros(PREPAD_SIZE*SCALE,PREPAD_SIZE*SCALE,numFiles,'double');
mandarinTest=zeros(PREPAD_SIZE*SCALE,PREPAD_SIZE*SCALE,numFiles,'double');
owlTest=zeros(PREPAD_SIZE*SCALE,PREPAD_SIZE*SCALE,numFiles,'double');
puffinTest=zeros(PREPAD_SIZE*SCALE,PREPAD_SIZE*SCALE,numFiles,'double');
toucanTest=zeros(PREPAD_SIZE*SCALE,PREPAD_SIZE*SCALE,numFiles,'double');
wood_duckTest=zeros(PREPAD_SIZE*SCALE,PREPAD_SIZE*SCALE,numFiles,'double');

for i = 1:numFiles
    im = imread([filePath,imList(i).name]);
    [rows, columns, colors] = size(im);
    
    A= padarray(im, [floor((PREPAD_SIZE-rows)/2) floor((PREPAD_SIZE-columns)/2)], 'replicate', 'pre');
    A= padarray(A, [ceil((PREPAD_SIZE-rows)/2) ceil((PREPAD_SIZE-columns)/2)], 'replicate', 'post');
    egretTest(:,:,i)= im2double(rgb2gray(imresize(A,SCALE)));
    
    originals{i}=im;
end

filePath = strcat('C:\Users\',username,'\Documents\MATLAB\Bird_Classifier\birds_testing\mandarin\');
imList=dir(fullfile(filePath,'*.jpg'));

for i = 1:numFiles
    im = imread([filePath,imList(i).name]);
    [rows, columns, colors] = size(im);
    
    A= padarray(im, [floor((PREPAD_SIZE-rows)/2) floor((PREPAD_SIZE-columns)/2)], 'replicate', 'pre');
    A= padarray(A, [ceil((PREPAD_SIZE-rows)/2) ceil((PREPAD_SIZE-columns)/2)], 'replicate', 'post');
    mandarinTest(:,:,i)= im2double(rgb2gray(imresize(A,SCALE)));
    
    originals{i+numFiles*1}=im;
end

filePath = strcat('C:\Users\',username,'\Documents\MATLAB\Bird_Classifier\birds_testing\owl\');
imList=dir(fullfile(filePath,'*.jpg'));

for i = 1:numFiles
    im = imread([filePath,imList(i).name]);
    [rows, columns, colors] = size(im);
    
    A= padarray(im, [floor((PREPAD_SIZE-rows)/2) floor((PREPAD_SIZE-columns)/2)], 'replicate', 'pre');
    A= padarray(A, [ceil((PREPAD_SIZE-rows)/2) ceil((PREPAD_SIZE-columns)/2)], 'replicate', 'post');
    owlTest(:,:,i)= im2double(rgb2gray(imresize(A,SCALE)));
    
    originals{i+numFiles*2}=im;
end

filePath = strcat('C:\Users\',username,'\Documents\MATLAB\Bird_Classifier\birds_testing\puffin\');
imList=dir(fullfile(filePath,'*.jpg'));

for i = 1:numFiles
    im = imread([filePath,imList(i).name]);
    [rows, columns, colors] = size(im);
    
    A= padarray(im, [floor((PREPAD_SIZE-rows)/2) floor((PREPAD_SIZE-columns)/2)], 'replicate', 'pre');
    A= padarray(A, [ceil((PREPAD_SIZE-rows)/2) ceil((PREPAD_SIZE-columns)/2)], 'replicate', 'post');
    puffinTest(:,:,i)= im2double(rgb2gray(imresize(A,SCALE)));
    
    originals{i+numFiles*3}=im;
end

filePath = strcat('C:\Users\',username,'\Documents\MATLAB\Bird_Classifier\birds_testing\toucan\');
imList=dir(fullfile(filePath,'*.jpg'));

for i = 1:numFiles
    im = imread([filePath,imList(i).name]);
    [rows, columns, colors] = size(im);
    
    A= padarray(im, [floor((PREPAD_SIZE-rows)/2) floor((PREPAD_SIZE-columns)/2)], 'replicate', 'pre');
    A= padarray(A, [ceil((PREPAD_SIZE-rows)/2) ceil((PREPAD_SIZE-columns)/2)], 'replicate', 'post');
    toucanTest(:,:,i)= im2double(rgb2gray(imresize(A,SCALE)));
    
    originals{i+numFiles*4}=im;
end

filePath = strcat('C:\Users\',username,'\Documents\MATLAB\Bird_Classifier\birds_testing\wood_duck\');
imList=dir(fullfile(filePath,'*.jpg'));

for i = 1:numFiles
    im = imread([filePath,imList(i).name]);
    [rows, columns, colors] = size(im);
    
    A= padarray(im, [floor((PREPAD_SIZE-rows)/2) floor((PREPAD_SIZE-columns)/2)], 'replicate', 'pre');
    A= padarray(A, [ceil((PREPAD_SIZE-rows)/2) ceil((PREPAD_SIZE-columns)/2)], 'replicate', 'post');
    wood_duckTest(:,:,i)= im2double(rgb2gray(imresize(A,SCALE)));
    
    originals{i+numFiles*5}=im;
end

disp('Test images compiled');