from numpy import linspace, complex128

negZ = -1e-12
posZ = 1e-12
def complex_grid(x_min=-10, x_max=10, y_min=-10, y_max=10, num=25):
	if (x_min < 0 and x_max > 0) or (y_min < 0 and y_max > 0):	
		neg_x_num = int((-x_min * num)/(x_max - x_min)) + 1
		pos_x_num = int((x_max * num)/(x_max - x_min))
		neg_y_num = int((-y_min * num)/(y_max - y_min)) + 1
		pos_y_num = int((y_max * num)/(y_max - y_min))
		return [
			[
				[[complex128(x + y * 1j) for x in linspace(x_min, negZ, neg_x_num)] for y in linspace(y_min, negZ, neg_y_num)],
				[[complex128(x + y * 1j) for y in linspace(y_min, negZ, neg_y_num)] for x in linspace(x_min, negZ, neg_x_num)]
			],
			[
				[[complex128(x + y * 1j) for x in linspace(posZ, x_max, pos_x_num)] for y in linspace(y_min, negZ, neg_y_num)],
				[[complex128(x + y * 1j) for y in linspace(y_min, negZ, neg_y_num)] for x in linspace(posZ, x_max, pos_x_num)]
			],
			[
				[[complex128(x + y * 1j) for x in linspace(posZ, x_max, pos_x_num)] for y in linspace(posZ, y_max, pos_y_num)],
				[[complex128(x + y * 1j) for y in linspace(posZ, y_max, pos_y_num)] for x in linspace(posZ, x_max, pos_x_num)]
			],
			[
				[[complex128(x + y * 1j) for x in linspace(x_min, negZ, neg_x_num)] for y in linspace(posZ, y_max, pos_y_num)],
				[[complex128(x + y * 1j) for y in linspace(posZ, y_max, pos_y_num)] for x in linspace(x_min, negZ, neg_x_num)]
			],
		]
	else:
		return [
			[[complex128(x + y * 1j) for x in linspace(x_min, x_max, num)] for y in linspace(y_min, y_max, num)],
			[[complex128(x + y * 1j) for y in linspace(x_min, x_max, num)] for x in linspace(y_min, y_max, num)]
		]	
