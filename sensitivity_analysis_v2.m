% Step 1: Define the model or function
net = mdls{1,1};

% Step 2: Define parameter ranges for each parameter column in X_train
paramRanges = [min(X_train.pandora), max(X_train.pandora);
               min(X_train.Direction), max(X_train.Direction);
               min(X_train.Speed), max(X_train.Speed);
               min(X_train.Temperature), max(X_train.Temperature);
               min(X_train.Humidity), max(X_train.Humidity);
               min(X_train.Pressure), max(X_train.Pressure);
               min(X_train.hour), max(X_train.hour);
              ];

% Step 3: Generate parameter samples using Monte Carlo sampling
N = 1000; % Number of samples
paramSamples = zeros(N, size(paramRanges, 1));
for i = 1:size(paramRanges, 1)
    paramSamples(:, i) = paramRanges(i, 1) + (paramRanges(i, 2) - paramRanges(i, 1)) * rand(N, 1);
end

% Step 4: Evaluate the model for each parameter sample
modelOutputs = zeros(N, 1);
for i = 1:N
    inputSample = paramSamples(i,:);
    modelOutputs(i) = net(inputSample');
end

% Step 5: Perform sensitivity analysis

%Calculate the mean of the model outputs (modelOutputs)
meanOutput = mean(modelOutputs);

%Calculate the total variance (totalVariance) of the model outputs
totalVariance = var(modelOutputs);

%Calculate the variance of the model outputs when one parameter is fixed while others vary (parameterVariance):
parameterVariance = zeros(1, size(paramSamples, 2));
for i = 1:size(paramSamples, 2)
    fixedParamSamples = paramSamples;
    fixedParamSamples(:, i) = mean(paramSamples(:, i));
    fixedOutputs = net(fixedParamSamples');
    parameterVariance(i) = var(fixedOutputs);
end

%Calculate the first-order sensitivity indices (firstOrderIndices)
firstOrderIndices = parameterVariance ./ totalVariance;

%Calculate the total-order sensitivity indices (totalOrderIndices)
%totalOrderIndices = (totalVariance - sum(parameterVariance)) ./ totalVariance;
totalOrderIndices = zeros(1, size(paramSamples, 2));
for i = 1:size(paramSamples, 2)
    fixedParamSamples = paramSamples;
    fixedParamSamples(:, i) = mean(paramSamples(:, i));
    fixedOutputs = net(fixedParamSamples');
    totalOrderIndices(i) = var(fixedOutputs);
end

%Add labels to the first order indices
paramNames = X_train.Properties.VariableNames;

% Create a table or cell array to store parameter names and first-order sensitivity indices
paramSensitivityTable = table(paramNames', firstOrderIndices', totalOrderIndices', 'VariableNames', {'Parameter', 'FirstOrderSensitivity','TotalOrderSensitivity'});

%save out the sensitivity table
writetable(paramSensitivityTable,'sensitivityanalysis.csv')