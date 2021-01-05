import numpy as np
from skimage import measure
from skimage.color import hsv2rgb as _hsv2rgb

NEG_Z = -1e-12
POS_Z = 1e-12

linear_point_set = np.linspace

def complex_grid(x_min=-10, x_max=10, y_min=-10, y_max=10, num=25):
	if (x_min < 0 and x_max > 0) or (y_min < 0 and y_max > 0):	
		return (*complex_grid(x_min, NEG_Z, y_min, NEG_Z, int(num/2)),
			*complex_grid(POS_Z, x_max, y_min, NEG_Z, int(num/2)),
			*complex_grid(x_min, NEG_Z, POS_Z, y_max, int(num/2)),
			*complex_grid(POS_Z, x_max, POS_Z, y_max, int(num/2)))

	x = np.linspace(x_min, x_max, num+1)
	y = np.linspace(y_min, y_max, num+1)
	X, Y = np.meshgrid(x,y)
	Z = X + 1j*Y

	return Z, np.transpose(Z)

def power(points, exponent):
	return np.power(points, exponent)

def times_table(factor, start=0, end=199):
	result = []
	
	for value in range(start, end):
		new_value = (value * factor) % end
		result.append([
			(np.cos(value * 2 * np.pi / end), np.sin(value * 2 * np.pi / end)),
			(np.cos(new_value * 2 * np.pi / end), np.sin(new_value * 2 * np.pi / end))
		])

	return result;

def elliptic_curve(q,p):
	x, y = np.ogrid[-12:12:100j, -12:12:100j]
	r = pow(y, 2) - pow(x, 3) - x * p - q

	# Find contours at a constant value of 0.8
	return measure.find_contours(r, 0)

def four_leaf_rose(q=4):
	x, y = np.ogrid[-12:12:100j, -12:12:100j]
	r = pow(pow(x, 2) + pow(y,2), 3) - q * pow(x, 2) * pow(y,2)
	return measure.find_contours(r, 0)


class PixelMap:
	pass

def _complex_pixels(position, size, step):
	x0, y0 = position
	w, h = size
	y = np.arange(y0 + h/2, y0 - h/2, -step)
	x = np.arange(x0 - w/2, x0 + w/2, step)
	Y, X = np.meshgrid(y,x)
	return X + 1j*Y

class DomainColors(PixelMap):
	def __call__(self, position, size, step, transform=None):
		Z = _complex_pixels(position, size, step)
		if transform:
			Z = transform(Z)
		H = np.angle(Z) % (2*np.pi)
		r = np.log2(1. + np.abs(Z))
		S = (1. + np.abs(np.sin(2. * np.pi * r))) / 2.
		V = (1. + np.abs(np.cos(2. * np.pi * r))) / 2.

		color_wheel = np.empty((Z.shape[0], Z.shape[1], 3), dtype=np.uint8)
		color_wheel[:, :, 0] = 255 * (H / H.max())
		color_wheel[:, :, 1] = 255 * S
		color_wheel[:, :, 2] = 255 * V

		return 255 * _hsv2rgb(color_wheel)

class MandlebrotSet(PixelMap):
	def __call__(self, position, size, step, iterations=80):
		C = _complex_pixels(position, size, step)
		C_size = C.shape[0], C.shape[1]
		Z = np.zeros(C_size, dtype=complex)
		M = np.full(C_size, True, dtype=bool)

		for i in range(iterations):
			Z[M] = Z[M] * Z[M] + C[M]
			M[np.abs(Z) > 2] = False

		M = np.uint8(M)
		R = np.empty((C_size[0], C_size[1], 3), dtype=np.uint8)
		R[:,:,0] = 255 * M
		R[:,:,1] = 255 * M
		R[:,:,2] = 255 * M
		return R	

domain_colors = DomainColors()
mandelbrot_set = MandlebrotSet()



def helix(t, as_points=False):
    result = np.cos(t), t, np.sin(t)
    return result if as_points else list(result)

def wireframe(x,y,fn):
    x_lines, y_lines = [], []
    for xval in x:
        temp = []
        for yval in y:
            temp.append( fn(xval,yval) )
        x_lines.append(temp)

    for yval in y:
        temp = []
        for xval in x:
            temp.append( fn(xval,yval) )
        y_lines.append(temp)

    return x_lines, y_lines

def surface(x,y,fn):
    return wireframe(x,y,fn)[1]

def curved_plane(x,y, as_wireframe=False):    
    result = wireframe(x,y, lambda x,y: (x,y*y,x*y))
    return result if as_wireframe else result[1]


def cylinder(pos=(0,0,0),radius=1,num=25, as_wireframe=False):
    result = wireframe(
        np.linspace(-radius,radius, num=num),
        np.linspace(0, 2*np.pi, num=num),
        lambda r,t: (pos[0] + np.cos(t), pos[1] + np.sin(t), pos[2] + r)
    )

    return result if as_wireframe else result[1]

def sphere(pos=(0,0,0),radius=1,num=12, as_wireframe=False):
    result = wireframe(
        np.linspace(-np.pi,np.pi, num=num),
        np.linspace(-np.pi,np.pi, num=num),
        lambda p,t: (pos[0] + radius*np.cos(t)*np.cos(p), pos[1] + radius*np.cos(t)*np.sin(p), pos[2] + radius*np.sin(t))
    )
    return result if as_wireframe else result[1]

