% Geração Gaussiana %
MedX = 10;
MedY = 20;
VX = 1;
VY = 1;
nRuns = 5000;
pontos = zeros(2,nRuns);

for jj = 1:nRuns
    pontos(:,jj) = [MedX+VX*randn() MedY+VY*randn()];
end

figure
plot(pontos(1,:), pontos(2,:), '.k')
hold on 
plot([MedX MedX],[MedY-5*VY MedY+5*VY],':r','LineWidth',1)
plot([MedX-5*VX MedX+5*VX],[MedY MedY],':r','LineWidth',1)
hold off
axis([MedX-5*VX MedX+5*VX MedY-5*VY MedY+5*VY])

%%
% Geração uniforme %
MedX = 10;
MedY = 20;
VX = 1;
VY = 1;
nRuns = 5000;
pontos = zeros(2,nRuns);

for jj = 1:nRuns
    pontos(:,jj) = [MedX+VX*rand() MedY+VY*rand()];
end

figure
plot(pontos(1,:), pontos(2,:), '.k')
hold on 
plot([MedX+VX/2 MedX+VX/2],[MedY-5*VY MedY+5*VY],':r','LineWidth',2)
plot([MedX-5*VX MedX+5*VX],[MedY+VY/2 MedY+VY/2],':r','LineWidth',2)
hold off
axis([MedX MedX+VX MedY MedY+VY])

%%
s1 = randn(100,1);
s2 = randn(100,1);
dista(s1,s2)

