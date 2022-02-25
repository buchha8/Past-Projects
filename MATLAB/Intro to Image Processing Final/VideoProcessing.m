%Logitech Camera
vid = videoinput('winvideo', 2, 'RGB24_640x480');
vid.FrameGrabInterval = 5;

set(vid, 'FramesPerTrigger', Inf);
set(vid, 'ReturnedColorspace', 'rgb');

%Define file outputs
myVideo1 = VideoWriter('Normal.avi');
myVideo1.FrameRate = 15;

myVideo2 = VideoWriter('BW.avi');
myVideo2.FrameRate = 15;

%start capturing video
start(vid);

%prepare files for writing
open(myVideo1);
open(myVideo2);

%Element for Morphological Image Processing used later
s1 = strel('disk', 5);

%capture video for a small period of time
while(vid.FramesAcquired <= 200)
    data = getsnapshot(vid);
    
    %Subtract by color, so only areas with high green/red will remain
    only_red = imsubtract(data(:,:,1), rgb2gray(data));
    only_green = imsubtract(data(:,:,2), rgb2gray(data));
    
    only_red = medfilt2(only_red,[3 3]);
    only_green = medfilt2(only_green,[3 3]);
    
    only_red = 255*uint8(im2bw(only_green,0.02));
    only_green = 255*uint8(im2bw(only_green,0.02));
    
    %use both green and red to minimize differences
    both = 255*uint8(only_green & only_red);
    
    %erode and dilate to remove noisiness
    botherode = imerode(both, s1);
    bothdilate = imdilate(botherode, s1);
    
    objects = bwlabel(bothdilate);
    objectstats = regionprops(objects,'BoundingBox','Centroid');
    
    imshow(data);
    hold on
    %Plot all bounding boxes
    for(i = 1:length(objectstats))
        box = objectstats(i).BoundingBox;
        centroid = objectstats(i).Centroid;
        rectangle('Position',box,'EdgeColor','y','LineWidth',3);
        plot(centroid(1),centroid(2),'-m+');

    end
    hold off
    
    %write to files
    writeVideo(myVideo1, data);
    writeVideo(myVideo2, bothdilate);
end

%stop recording, stop writing, and clear data
stop(vid);
close(myVideo1);
close(myVideo2);
clear all;