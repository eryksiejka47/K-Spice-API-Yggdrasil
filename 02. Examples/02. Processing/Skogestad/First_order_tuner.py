delay = 0
tau_1 = 14

y_max = 47.8
y_min = 45
y_delta = y_max - y_min

u_min = 16.31
u_max = 18.12
u_delta = u_max - u_min

k = y_delta/u_delta
k_mark = k/tau_1

tau_c = float(input("Enter tuning constant tau_c:"))

kc = (1/k)*(tau_1/(tau_c + delay))

tau_i_1 = tau_1
tau_i_2 = 4*(tau_c + delay)

if tau_i_1 > tau_i_2:
    tau_i = tau_i_2
else:
    tau_i = tau_i_1

print("Proportional Gain: ", kc)
print("Integral time: ", tau_i)

