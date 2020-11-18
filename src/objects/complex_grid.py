from numpy import linspace, complex128

negZ = -1e-12
posZ = 1e-12
def complex_grid(x_min=-10, x_max=10, y_min=-10, y_max=10, num=25):
	if (x_min < 0 and x_max > 0) or (y_min < 0 and y_max > 0):	
		return [
			[
				[[complex128(x + y * 1j) for x in linspace(x_min, negZ, num)] for y in linspace(y_min, negZ, num)],
				[[complex128(x + y * 1j) for y in linspace(y_min, negZ, num)] for x in linspace(x_min, negZ, num)]
			],
			[
				[[complex128(x + y * 1j) for x in linspace(posZ, x_max, num)] for y in linspace(y_min, negZ, num)],
				[[complex128(x + y * 1j) for y in linspace(y_min, negZ, num)] for x in linspace(posZ, x_max, num)]
			],
			[
				[[complex128(x + y * 1j) for x in linspace(posZ, x_max, num)] for y in linspace(posZ, y_max, num)],
				[[complex128(x + y * 1j) for y in linspace(posZ, y_max, num)] for x in linspace(posZ, x_max, num)]
			],
			[
				[[complex128(x + y * 1j) for x in linspace(x_min, negZ, num)] for y in linspace(posZ, y_max, num)],
				[[complex128(x + y * 1j) for y in linspace(posZ, y_max, num)] for x in linspace(x_min, negZ, num)]
			],
		]
	else:
		return [
			[[complex128(x + y * 1j) for x in linspace(x_min, x_max, num)] for y in linspace(y_min, y_max, num)],
			[[complex128(x + y * 1j) for y in linspace(x_min, x_max, num)] for x in linspace(y_min, y_max, num)]
		]	
