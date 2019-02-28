#!/usr/local/bin/octave -qf

arg_list = argv();
filename = arg_list{1};
% printf("'%s'", filename);
d = load("-ascii", filename);

b = d(:, 1);
p = d(:, 2);
v = d(:, 3);
t = [1:size(d, 1)];

hf = figure();
hold on;
plot(t, b, 'k.');
plot(t, p ./ b, 'rx');
xlabel("date");
plot(t, v, 'b+');
plot(t, p, 'gx');
legend("BV", "P/B", "Vol(0.1B¥)", "Price(¥)");
print(hf, [ filename ".svg" ], "-dsvg");
hold off;
%pause();
