%Bird_Classifier, Alexander Buchholz
%This file contains all training and classification code
Initialize_Data;

X=cat(3, egretX, mandarinX, owlX, puffinX, toucanX, wood_duckX);
Test=cat(3, egretTest, mandarinTest, owlTest, puffinTest, toucanTest, wood_duckTest);
sizeX = size(X);
%target vector classes are in alphabetical order: 
%Egret, Mandarin, Owl, Puffin, Toucan, Wood Duck
T=[-ones(6, sizeX(1),sizeX(3))];
T(1,:,1:sizeX(3)/6)=1;
T(2,:,sizeX(3)/6:2*sizeX(3)/6)=1;
T(3,:,2*sizeX(3)/6:3*sizeX(3)/6)=1;
T(4,:,3*sizeX(3)/6:4*sizeX(3)/6)=1;
T(5,:,4*sizeX(3)/6:5*sizeX(3)/6)=1;
T(6,:,5*sizeX(3)/6:6*sizeX(3)/6)=1;

meanX=sum(X,3)/sizeX(3);
stdX=std(X,0,3);

for i = 1:sizeX(3)
    X(:,:,i)=((X(:,:,i)-meanX(:,:))./stdX(:,:));
end


theta=100; % criterion to stop
eta=0.01; % step size
Nh=10;  % number of hidden nodes
Ni=PREPAD_SIZE*SCALE; % dimension of input vector = number of input nodes
No=6; % number of class = number of out nodes

%initialization of weights
wji=ones(Nh,Ni);
for j=1:Nh
    for i=1:Ni
        wji(j,i)=2*(rand()-.5)*(1/sqrt(Ni));
    end
end

wkj=ones(No,Nh);
for k=1:No
    for j=1:Nh
        wkj(k,j)=2*(rand()-.5)*(1/sqrt(Nh));
    end
end

J=theta+1;
iteration=0;
%main training loop
disp('Begin training');
while J > theta
    r_index=round(sizeX(3)*rand()+0.5);
    %Note that, because netj appears in the exponents of the activation
    %denominator, netj was scaled down to avoid large exponents. Large
    %exponents create floating point rounding errors, division by zero, and
    %cause "NaN" to populate all matrices.
    netj=[ones(Nh,1),wji]*[ones(1,Ni); X(:,:,r_index)]./100;
    %Initialization
    sizeJ=size(netj);
    Y=ones(sizeJ);
    derY=ones(sizeJ);
    for m=1:sizeJ(1)
        for n=1:sizeJ(2)
            %Activation Function
            Y(m,n)=1.716*((exp((2/3)*netj(m,n))-exp((-2/3)*netj(m,n)))/(exp((2/3)*netj(m,n))+exp((-2/3)*netj(m,n))));
            derY(m,n)=1.716*(2/(exp((2/3)*netj(m,n))+exp((-2/3)*netj(m,n)))).^2;
        end
    end

    netk=[ones(No,1),wkj]*[ones(1,Ni);Y];
    %Initialization
    sizeK=size(netk);
    Z=ones(sizeK);
    derZ=ones(sizeK);
    for m=1:sizeK(1)
        for n=1:sizeK(2)
            %Activation Function
            Z(m,n)=1.716*((exp((2/3)*netk(m,n))-exp((-2/3)*netk(m,n)))/(exp((2/3)*netk(m,n))+exp((-2/3)*netk(m,n))));
            derZ(m,n)=1.716*(2/(exp((2/3)*netk(m,n))+exp((-2/3)*netk(m,n)))).^2;
        end
    end

    delta_k=(T(:,:,r_index)-Z).*derZ;
    delta_j=wkj'*delta_k.*derY;

    wkj=wkj+eta*delta_k*Y';
    wji=wji+(eta*X(:,:,r_index)*delta_j')';

    J=(1/2)*(norm(T(:,:,r_index)-Z).^2);
    %Counter used for information only
    iteration=iteration+1;
end
disp('Training complete');

%Classify test images
sizeTest = size(Test);
meanTest=sum(Test,3)/sizeTest(3);
stdTest=std(Test,0,3);

for i = 1:sizeTest(3)
    Test(:,:,i)=((Test(:,:,i)-meanTest(:,:))./stdTest(:,:));
end

for i=1:sizeTest(3)
    %Note that, because netj appears in the exponents of the activation
    %denominator, netj was scaled down to avoid large exponents. Large
    %exponents create floating point rounding errors, division by zero, and
    %cause "NaN" to populate all matrices.
    netj=[ones(Nh,1),wji]*[ones(1,Ni); Test(:,:,i)]./100;
    sizeJ=size(netj);
    Y=ones(sizeJ);
    for m=1:sizeJ(1)
        for n=1:sizeJ(2)
            Y(m,n)=1.716*((exp((2/3)*netj(m,n))-exp((-2/3)*netj(m,n)))/(exp((2/3)*netj(m,n))+exp((-2/3)*netj(m,n))));
        end
    end

    netk=[ones(No,1),wkj]*[ones(1,Ni);Y];
    sizeK=size(netk);
    Z=ones(sizeK);
    for m=1:sizeK(1)
        for n=1:sizeK(2)
            Z(m,n)=1.716*((exp((2/3)*netk(m,n))-exp((-2/3)*netk(m,n)))/(exp((2/3)*netk(m,n))+exp((-2/3)*netk(m,n))));
        end
    end
    %Vector containing distance to all classes
    summary = [norm(T(:,:,1)-Z).^2;
                norm(T(:,:,1*sizeX(3)/6)-Z).^2
                norm(T(:,:,2*sizeX(3)/6)-Z).^2
                norm(T(:,:,3*sizeX(3)/6)-Z).^2
                norm(T(:,:,4*sizeX(3)/6)-Z).^2
                norm(T(:,:,5*sizeX(3)/6)-Z).^2];
    
    [value, class] = min(summary);
   
    %Write to appropriate repository depending on classification
    if class==1
        imwrite(originals{i}, strcat('C:\Users\',username,'\Documents\MATLAB\Bird_Classifier\birds_classified\egret\bird',num2str(i),'.jpg'),'jpg');
    elseif class==2
        imwrite(originals{i}, strcat('C:\Users\',username,'\Documents\MATLAB\Bird_Classifier\birds_classified\mandarin\bird',num2str(i),'.jpg'),'jpg');
    elseif class==3
        imwrite(originals{i}, strcat('C:\Users\',username,'\Documents\MATLAB\Bird_Classifier\birds_classified\owl\bird',num2str(i),'.jpg'),'jpg');
    elseif class==4
        imwrite(originals{i}, strcat('C:\Users\',username,'\Documents\MATLAB\Bird_Classifier\birds_classified\puffin\bird',num2str(i),'.jpg'),'jpg');
    elseif class==5
        imwrite(originals{i}, strcat('C:\Users\',username,'\Documents\MATLAB\Bird_Classifier\birds_classified\toucan\bird',num2str(i),'.jpg'),'jpg');
    else
        imwrite(originals{i}, strcat('C:\Users\',username,'\Documents\MATLAB\Bird_Classifier\birds_classified\wood_duck\bird',num2str(i),'.jpg'),'jpg');
    end

end
disp('Classifying complete');