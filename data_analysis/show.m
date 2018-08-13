#!/usr/local/bin/octave -qf

arg_list = argv();
filename = arg_list{1};
% printf("'%s'", filename);
d = load("-ascii", filename);

b = d(:, 1);
p = d(:, 2);
v = d(:, 3);
t = [1:size(d, 1)];

figure 1;
hold on;
plot(t, p ./ b, 'rx');
xlabel("date");
plot(t, v, 'bo');
plot(t, p, 'gd');
legend("P/B", "Vol(0.1B¥)", "Price(¥)");
hold off;
pause();
