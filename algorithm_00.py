
# This below worked but I hatted it, also I figured it was better for the control calc to be in a separate file
# So copy pasted the original here for reference but from now on all control calc will done in a 
# separate class


try:
		loop_start_time = datetime.now()
		cpu.get_data()
		sub_count += 0.001
		count_for_WD = int(100*(config.scan_count + sub_count))
		try_throttle_calc = 100 * (cpu.temp - config.min_temp)/(config.max_temp - config.min_temp)
		try_throttle_calc_smoothed = try_throttle_calc_smoothed + 0.1*(try_throttle_calc - try_throttle_calc_smoothed)
		change = cpu.temp - last_cpu_temp
		if change > 1.1:
			print("---------------- Big CTemp Increase : ",last_cpu_temp, " to ",cpu.temp, " so ", change)
		last_cpu_temp = cpu.temp
	
		# Check CPU temperature situation to use in below IF  statements
		# Display data occasionally
		c_or_1 = sub_count >= 0.998
		# Turn off Fan when on and below target range
		c_or_2 = (throttle > 0) and (cpu.temp<lower_min_temp)  # e.g. if using 61 to 69 then 57
		# Turn fan on when temperature increasing fast
		c_or_3 = (change > 2.1) and (cpu.temp > lower_mid_temp)# e.g. if using 61 to 69 then 63
		# Turn fan on when temperature approaching top of target range.
		c_or_4 = cpu.temp >= upper_mid_temp 				   # e.g. if using 61 to 69 then 67	
	
		if c_or_1 or c_or_2 or c_or_3 or c_or_4:
	
			buffer_increment_flag = True
	
			cpu.calc_averages()
	
			if cpu.temp >= config.max_temp:
				throttle = 100
			elif cpu.temp<= config.min_temp:
				throttle = 0
			elif cpu.temp >= upper_mid_temp:
				# use lastest info when temperature high
				throttle = try_throttle_calc
			elif try_throttle_calc_smoothed > 0:
				# use smoothed data when temperature lower and smoother value over zero
				throttle = try_throttle_calc_smoothed
			else:
				throttle = 6
	
			if throttle <= 0 :
				speed = 0
				freq = config.min_freq
			else:
				speed = config.min_speed + (throttle*(config.max_speed-config.min_speed)/100)
				freq = config.max_freq
	
cpu.set_pwm_control_fan(freq,speed)
